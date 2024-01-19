import json
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
    print(profile.fmt_grid() + '\n')

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

    experiment_2()

    print('Done')
