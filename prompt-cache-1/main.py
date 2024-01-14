import json
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

model_path = '../../data/llama-2-7b.Q4_K_M.gguf'

# default example
default_prompt = """The mouse's name is David and is 12 years old."""
default_questions = [
    "Question: What is the mouse's name? Answer:",
    "Question: How old is the mouse? Answer:",
]

# globals used for these methods within the functions
# e.g. llm.sample(**params_llm_sample)
# change here, or in __main__ section before calling main function
params_llm_eval = {}
params_llm_sample = {
    'temp': 0.0,
}

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
    profile.add('eval_prompt')
    # Seed (if set) must be after eval
    if seed is not None: llm.set_seed(seed)
    # Completion Section
    counter = 0
    token = llm.sample(**params_llm_sample)
    while token is not llm.token_eos() :
        counter += 1
        if counter > max_tokens: break
        if verbose > 0:
            print(llm.detokenize([token]).decode(), 
                  end='', flush=True)
        llm.eval([token])
        token = llm.sample()
    profile.add('main_sample')
    print('\n' + profile.dumps())

@suppress_stderr
def create_state(
        llm:Llama, 
        prefix:str,
    ) -> LlamaState:
    profile = ProfileStats()
    llm.reset()
    profile.add('reset')
    _ = llm.eval(llm.tokenize(prefix.encode()))
    profile.add('eval_time')
    state = llm.save_state()
    profile.add('save_state')
    print(profile.dumps())
    return state

# main demonstration functions ---------

@suppress_stderr
def main(
    prompt:str,
    questions:list,
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
    
# scripting ------

def warmup_msg(text:str) -> None:
    estimate_tok_per_sec = 6 # config for your machine
    num_tokens = len(tokenize_text(model_path, text))
    warmup_secs = int(num_tokens / estimate_tok_per_sec)
    msg = f'Estimated ~{warmup_secs} secs to cache prompt ...'
    print(msg)
    

if __name__ == '__main__':
    
    # Small example: default prompt/question
    prompt = default_prompt
    questions = default_questions
    params_llm_sample = {'temp': 1.0}
    print('#### Starting default example:')
    warmup_msg(prompt)
    main(
        prompt,
        questions,
        n_tries=1, 
        max_tokens=10,
        seed=None,
        verbose=1,
    )

    # import sys
    # sys.exit(0)

    # Larger example: FAA questions
    data_fn = './data/faa.json'
    data = json.load(open(data_fn, 'r'))
    prompt = data['prompt']
    questions = data['questions']
    params_llm_sample = {'temp': 1.0}
    print('#### Starting FAA example:')
    warmup_msg(prompt)
    main(
        prompt,
        questions,
        n_tries=2, 
        max_tokens=30,
        seed=None,
        verbose=1,
    )
    
    print('Done')
