# PyLlama Scripts

Utilies, Scripts, and Experiments for using LlamaCpp / PythonLlamaCpp

## Contents
 - **[Prompt Caching Demo](./prompt-cache-1/)** - using low-level-api to analyze the the accuracy and performance of prompt caching
 - **[Benchmarking Script](./benchmark-app-1/)** - bash and python scripts for timing and performance using high-level-api.
 - **[Notebooks](./nbs/)** - various experiments around llama inference and configuration.


### [Prompt Caching Demo](./prompt-cache-1/)

Prompt caching is a technique for speeding up the completion of a prompt by caching the results of previous completions. This is a demonstration app for the technique.

Create system_prompt + questions in [`data/`](./prompt-cache-1/data/) with `mkjson.py` to create  a `<data-name>.json` file.

Configure bottom scripting section of `main.py` like:

```python
data_fn = './data/faa-mistral.json'
data = json.load(open(data_fn, 'r'))
prompt = data['prompt']
questions = data['questions']
params_llm_sample = {'temp': 0.0}
print('#### Starting FAA example (mistral-hf formatted):')
warmup_msg(prompt)
main(
    prompt,
    questions,
    n_tries=3, 
    max_tokens=30,
    seed=None,
    verbose=2,
)

print('Done')
```

And run `>python main.py` to produce [logs](./prompt-cache-1/output/) like:

```
#### Starting FAA example (mistral-hf formatted):
Estimated ~31 secs to cache prompt ...
{
  "reset": "0.00",
  "eval_time": "19.92",
  "save_state": "0.08"
}
### Saved Cache State
## Question 0: 
Question: What was the destination of the plane? [/INST]
# Trial 0:
 The original destination of Alaska Airlines Flight 1282 was Ontario, California.
{
  "load_state": "0.04",
  "eval_prompt": "2.23",
  "main_sample": "2.73"
}
# Trial 1:
 The destination of the plane was Ontario, California.
{
  "load_state": "0.03",
  "eval_prompt": "2.24",
  "main_sample": "1.78"
}
```

### [Benchmarking Script](./benchmark-app-1/)

*Current data reflect run of v0.2.19 on Debian cpu-only*

- Use `cpp-script.sh` to invoke llama-cpp.
- Use `py-script.sh` to which will call `main.py` which use python-llama-cpp.

```
$ ./cpp-script.sh 
script #1 done
script #2 done
script #3 done
script #1 done
script #2 done
script #3 done
all scripts done. each output logs appended to data/time-script-3thread.log
```

For example this will create [log files](./benchmark-app-1/data/) like:

```
...
llama_print_timings:       total time =   15271.65 ms
### MODEL_NUM: 1 | ITER: 1 ###
time_load:   11.7
time_infer:  11.5
time_script: 23.3
comp_tokens: 50
N_THREADS:   3
MAX_TOKENS:  50
model_fn:    /mnt/disk2/llamas/TheBloke7B/llama-2-7b.Q4_K_M.gguf
output:      1. everyone knows they’re Jupiter and Saturn and Uranus B. 2.
...
```