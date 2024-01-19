import json
import time
import pickle
from typing import (
    Dict,
    List,
)
from llama_cpp import (
    Llama,
    LlamaState,
)
from utils import (
    suppress_stderr,
    llama_log_obj,
    tokenize_text,
    ProfileStats,
)

# model_path = '../../../alpha-app/data/llama-2-7b.Q4_K_M.gguf'
model_path = '../../../../data/mistral-7b-instruct-v0.2.Q4_K_M.gguf'

# default example
default_prompt = """<s>[INST] The mouse's name is David and is 12 years old."""
default_questions = [
    "Question: What is the mouse's name? [/INST]",
    "Question: How old is the mouse? [/INST]",
]

# globals used for these methods within the functions
# e.g. llm.sample(**params_llm_sample)
# change here, or in __main__ section before calling main function
params_llm_eval = {}
params_llm_sample = {
    'temp': 0.0,
}

full_log = {}

# main building block functions ------

def question_cached_state(
        llm:Llama,
        cached_state:LlamaState,
        question_text:str,
        max_tokens:int=10,
        seed:int=None,
        verbose:int=1,
        suppress_stats:bool=False,
    ) -> None:
    profile = ProfileStats()
    # Setup Section
    llm.load_state(cached_state)
    profile.add('load_state')
    tokens_question = llm.tokenize((question_text).encode())
    llm.eval(tokens_question)
    profile.add('eval_prompt', llm=llm)
    # Seed (if set) must be after eval
    if seed is not None: llm.set_seed(seed)
    # Completion Section
    counter = 0
    token = llm.sample(**params_llm_sample)
    while token is not llm.token_eos() :
        if counter >= max_tokens: break
        counter += 1
        if verbose > 0:
            print(llm.detokenize([token]).decode(), 
                  end='', flush=True)
        llm.eval([token])
        token = llm.sample()
    profile.add('main_sample', num_tokens=counter)
    print('\n')  # finish the flush
    if not(suppress_stats): print(profile.fmt_grid() + '\n')

@suppress_stderr
def create_state(
        llm:Llama, 
        prefix:str,
        verbose:int=1,
    ) -> LlamaState:
    profile = ProfileStats()
    llm.reset()
    profile.add('reset')
    prefix_tokenized = llm.tokenize(prefix.encode())
    _ = llm.eval(prefix_tokenized)
    profile.add('eval_time', num_tokens=len(prefix_tokenized))
    state = llm.save_state()
    profile.add('save_state')
    if verbose: print('\n' + profile.fmt_grid() + '\n')
    return state

@suppress_stderr
def load_base_apply_current(
        llm:Llama,
        base_fn:str,
        current_info:str,
        verbose:bool=True,
    ) -> LlamaState:
    '''
    Load base state from disk, apply current info, return state obj
    '''
    t0 = time.time()
    llm.reset()
    with open(base_fn, 'rb') as f:
        llm.load_state(pickle.load(f))
    if verbose: print(f'Loaded base_states from disk: {time.time()-t0:.2f}')
    # eval current on top of base_state, save to states obj
    t0 = time.time()
    current_tokenized = llm.tokenize(current_info.encode())
    _ = llm.eval(current_tokenized)
    state = llm.save_state()
    if verbose: print(f'Eval current info: {time.time()-t0:.2f}')
    return state

# main demonstration functions ---------

@suppress_stderr
def one_state_many_questions(
    prompt:str,
    questions:List[str],
    n_tries:int=1,
    max_tokens:int=30,
    seed:int=None,
    verbose:int=1,
    ) -> None:
    llm = Llama(
        model_path=model_path, 
    )
    cached_state = create_state(llm, prompt)
    if verbose > 0: print('### Saved Cache State')
    for question_num, question in enumerate(questions):
        if verbose > 0: 
            print(f'## Question {question_num}: {question}')
        for trial_num in range(n_tries):
            if verbose > 0:
                print(f'# Trial {trial_num}:')
            question_cached_state(
                llm, 
                cached_state, 
                question, 
                max_tokens=max_tokens,
                seed=seed,
                verbose=verbose,
            )
    if verbose >= 2:
        log_text = '\n'.join(llama_log_obj)
        print(f'### Global Log\n{log_text}')
    return
    

@suppress_stderr
def many_state_many_questions(
    assistants:Dict[str, str],  # <resturant-id>,<prompt>
    questions:List[Dict[str, str]],
    max_tokens:int=30,
    verbose:int=1,
    ) -> None:
    llm = Llama(
        model_path=model_path, 
    )
    states = {
        k: create_state(llm, v, verbose=1)
        for k,v in assistants.items()
    }
    for question in questions:
        print(f'## Question: {question}')
        question_cached_state(
            llm,
            states.get(question.get('id')),
            question.get('message'),
            max_tokens=max_tokens,
            verbose=verbose,
        )
    
def current_state_updating(
    base_state_fns:Dict[str, str],
    questions:List[Dict[str, str]],
    current_prompts:Dict[str, str],
    max_tokens:int=30,
    seed:int=None,
    verbose:bool=True,
    ) -> None:
    
    llm = Llama(
        model_path=model_path, 
    )
    
    states = {}

    # iterate over all current prompts
    for current_key in current_prompts.keys():

        print(f'### Current Key: {current_key}')
        current_info = current_prompts[current_key]
        print('------' + current_info + '\n------')
        current_info += "\n\nCustomer message:"
        
        # update in-mem states with current info
        for k,fn in base_state_fns.items():
            states[k] = load_base_apply_current(
                llm,
                fn,
                current_info,
                verbose=verbose,
            )
        print('------\n')

        # run questions at this current state
        for q in questions:
            print(f'## ID: {q.get("id")} | Question: {q.get("message")}')
            question_cached_state(
                llm,
                states.get(q.get('id')),
                q.get('message'),
                max_tokens=max_tokens,
                seed=seed,
                verbose=verbose,
                suppress_stats=True,  # toggle for profiling logs
            )


    pass

# scripting ------

def warmup_msg(text:str) -> None:
    estimate_tok_per_sec = 6 # config for your machine
    num_tokens = len(tokenize_text(model_path, text))
    warmup_secs = int(num_tokens / estimate_tok_per_sec)
    msg = f'Estimated ~{warmup_secs} secs to cache prompt ...'
    print(msg)

def wrap_instruct(text:str, obj:str='prompt') -> str:
    if obj == 'prompt':
        return f'<s>[INST] {text}'
    elif obj == 'question':
        return f'{text} [/INST]'
    return text

# experiments ------

@suppress_stderr
def experiment_3() -> None:
    
    # food2 example: restaurants A & B with incoming messages
    #                and updating current_info into cached state
    print('#### Starting food2 example (updating current_info):')
    
    b_overwrite_cache = False
    base_prompt_a_fn = './data/food2-prompt-a.txt'
    base_prompt_b_fn = './data/food2-prompt-b.txt'
    questions_fn = './data/food2-questions.json'
    state_fn_a = './saved_states/food2/state-a.pickle'
    state_fn_b = './saved_states/food2/state-b.pickle'
    
    current_prompts = {
        '3pm': '''\n - It is currently 3pm on Monday.\n - All Items are available currently''',
        '6pm': '''\n - It is currently 6pm on Monday.\n - Blue cheese is not available currently''',
        '10pm': '''\n - It is currently 10pm on Monday.\n - All Items are available currently''',
        # try concept of "86th" item
    }
    
    base_state_fns = {
        'a': state_fn_a,
        'b': state_fn_b,
    }

    questions = json.load(open(questions_fn, 'r'))
    
    questions = [
        {
            'id': q.get('id'),
            'message': wrap_instruct(q.get('message'), obj='question'),
        }
        for q in questions
    ]

    # current_state_updating will load these states from disk
    # no need to create them if they exist on most recent base_prompt
    if b_overwrite_cache:
        print('#### Creating new cache states')
        prompt_a = open(base_prompt_a_fn, 'r').read()
        prompt_b = open(base_prompt_b_fn, 'r').read()
        verbose = 1
        warmup_msg(prompt_a + prompt_b)
        llm = Llama(model_path)
        llm_state = create_state(
                        llm, 
                        wrap_instruct(prompt_a, obj='prompt'), 
                        verbose=verbose)
        with open(state_fn_a, 'wb') as f:
            pickle.dump(llm_state, f)
        llm = Llama(model_path)
        llm_state = create_state(
                        llm, 
                        wrap_instruct(prompt_b, obj='prompt'), 
                        verbose=verbose)
        with open(state_fn_b, 'wb') as f:
            pickle.dump(llm_state, f)

    current_state_updating(
        base_state_fns,
        questions,
        current_prompts,
        max_tokens=60,
        seed=None,
        verbose=1,
    )

    print('#### Starting food example:')

def experiment_2() -> None:
    
    # food example: restaurants A & B with incoming messages
    prompt_a_fn = './data/food-prompt-a.txt'
    prompt_b_fn = './data/food-prompt-b.txt'
    questions_fn = './data/food-questions.json'
    params_llm_sample = {'temp': 0.0}
    
    prompt_a = open(prompt_a_fn, 'r').read()
    prompt_b = open(prompt_b_fn, 'r').read()
    questions = json.load(open(questions_fn, 'r'))
    
    assistants = {
        'a': wrap_instruct(prompt_a, obj='prompt'),
        'b': wrap_instruct(prompt_b, obj='prompt'),
    }
    questions = [
        {
            'id': q.get('id'),
            'message': wrap_instruct(q.get('message'), obj='question'),
        }
        for q in questions
    ]

    print('#### Starting food example:')
    warmup_msg(prompt_a + prompt_b)

    many_state_many_questions(
        assistants,
        questions,
        max_tokens=60,
        verbose=1,
    )

def experiment_1() -> None:

    # # Small example: default prompt/question
    prompt = default_prompt
    questions = default_questions
    params_llm_sample = {'temp': 1.0}
    print('#### Starting default example:')
    warmup_msg(prompt)
    one_state_many_questions(
        prompt,
        questions,
        n_tries=2,
        max_tokens=10,
        seed=None,
        verbose=1,
    )

    # import sys
    # sys.exit(0)

    # Larger example: FAA questions
    data_fn = './data/faa-mistral.json'
    data = json.load(open(data_fn, 'r'))
    prompt = data['prompt']
    questions = data['questions']
    params_llm_sample = {'temp': 0.0}
    print('#### Starting FAA example (mistral-hf formatted):')
    warmup_msg(prompt)
    one_state_many_questions(
        prompt,
        questions,
        n_tries=3, 
        max_tokens=30,
        seed=None,
        verbose=1,
    )


if __name__ == '__main__':

    # experiment_1()
    # experiment_2()
    experiment_3()

    print('Done')
