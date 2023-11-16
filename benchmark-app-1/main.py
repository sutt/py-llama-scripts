import sys
import time
import argparse
import json
import llama_cpp
from llama_cpp import Llama
from llama_cpp import Completion

MODEL_FN_1  = '/mnt/disk2/llamas/TheBloke7B/llama-2-7b.Q4_K_M.gguf'
MODEL_FN_2  = '/mnt/disk2/llamas/mistral-7B-v0.1/ggml-model-q4_0.gguf'
LOG_PREFIX  = '>>>> '

def run_model(
    model_num = 1,
    iter_num = -1,
    n_threads = None,
    max_tokens = 50,
    question = 'Q: What are the three largest planets? A: ',
    model_params = {
        'temperature':  0.8,
        'max_tokens':   50,
    },
    ):

    model_fn = MODEL_FN_1 if model_num == 1 else MODEL_FN_2

    t0_script = time.time()

    t0_load = time.time()

    llm = Llama(
        model_path=model_fn, 
        n_threads=n_threads,
    )

    time_load = time.time() - t0_load

    t0_infer = time.time()

    output = llm(
                prompt=question,
                **model_params,
    )


    time_infer = time.time() - t0_infer

    time_script = time.time() - t0_script

    pre = LOG_PREFIX

    print(f"{pre}### MODEL_NUM: {model_num} | ITER: {iter_num} ###")
    print(f"{pre}time_load:   {round(time_load, 1)}")
    print(f"{pre}time_infer:  {round(time_infer, 1)}")
    print(f"{pre}time_script: {round(time_script, 1)}")
    print(f"{pre}comp_tokens: {output['usage']['completion_tokens']}")
    print(f"{pre}N_THREADS:   {n_threads}")
    print(f"{pre}MAX_TOKENS:  {max_tokens}")
    print(f"{pre}model_fn:    {model_fn}")
    print(f"{pre}output:      {output['choices'][0]['text']}")
    
    # print(json.dumps(output, indent=2))

def summarize(log_fn):
    with open(log_fn, 'r') as f:
        lines = f.readlines()
    lines = [line for line in lines if line.startswith(LOG_PREFIX)]
    lines = [line.replace(LOG_PREFIX, '') for line in lines]
    lines = [line.replace("### ", '\n### ') for line in lines]
    print(''.join(lines))


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_num', type=int, default=1)
    parser.add_argument('--iter_num', type=int, default=-1)
    parser.add_argument('--summarize', type=str, default=None)
    args = parser.parse_args()
    
    if not args.summarize:
        run_model(
            model_num = args.model_num,
            iter_num = args.iter_num,
        )
    else:
        summarize(args.summarize)

    







