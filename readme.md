# Profiling Python Llama Cpp


When building an LLM-based app, or building resarch-oriented pipelines It's convenient to manipulate the i/o, control flow and parameters in python (rather than bash script or cli as with original llama) This means we need this bridge library: `llama-cpp-python` which isn't just a wrapper to the executable's cli, but acutally compiles it's own executable, a clone of llama cpp. This separate compilation step on python + ctypes styke means it might be less performant than original llama.cpp (indeed we demonstrate between 10-40% less performance on naive install of the package) because it doesn't make optimal use of the target machine's architecture.


Ram Caching of the model weights creates a very user friendly experience when repetitively trying to run test inferences on the model, this almost completely eliminates 

Performance Gap between Python and C++:
 - For Llama2-7b_Q4 there's a 10 - 30% speedup on C++
 - For Mistral-7B-v0.1 there's a 20 - 40% speedup on C++

There's about a 5-10% speedup from using -t 4 over -t 2 on C++

Seeing slighlty better via more consistent / less variable results (esp on Mistral ) with n_threads=None over n_threads=3

One thing that happend is now all my models are getting cached in ram, so even by switching models I can't get > 1 sec load times in iteration #1.
 [x] try killing terminal that have launched a process before? Even that doesn't knock out the ram cache.
 [ ] try loading a larger model (13b?) to overflow cache

Still A lot I don't understand about how this package: how it fits into one running process (?), software engineering patterns that enable compiling of .py defined program plus binding those datastructures to python api, and the execution in linux environment. 

Another thing that doesn't really make sense is the CPU > 50% on py-llama seems counterproductive or at least not useful. is this seen in the llama.cpp n_thread

**Note:** the main.xxxxx.log will contain the top10 for each next-token prediction, e.g. this one.

```
[1699934528] top 10 candidates:
[1699934528]  -   302: '          of' (0.503)
[1699934528]  - 28705: '            ' (0.294)
[1699934528]  -   684: '       about' (0.047)
[1699934528]  -  6530: '       equal' (0.029)
[1699934528]  -   369: '        that' (0.026)
[1699934528]  - 10870: ' approximately' (0.009)
[1699934528]  -  5597: '      nearly' (0.009)
[1699934528]  -  2779: '      almost' (0.007)
[1699934528]  -   680: '        more' (0.006)
[1699934528]  -  5435: '       eight' (0.006)
[1699934528] sampled token:   302: ' of'
```

### Results of running the `time-script.sh` script

```bash
(venv) wsutt@gopher-worker-1:~/llama-cpp/py-llama/alpha-app/pkgs$ ./time-script.sh 
script #1 done
script #2 done
script #3 done
script #1 done
script #2 done
script #3 done
all scripts done. each output logs appended to data/time-script-3thread.log

### MODEL_NUM: 1 | ITER: 1 ###
time_load:   11.7
time_infer:  11.5
time_script: 23.3
comp_tokens: 50
N_THREADS:   3
MAX_TOKENS:  50
model_fn:    /mnt/disk2/llamas/TheBloke7B/llama-2-7b.Q4_K_M.gguf
output:      1. everyone knows they’re Jupiter and Saturn and Uranus B. 2.

### MODEL_NUM: 1 | ITER: 2 ###
time_load:   0.2
time_infer:  11.4
time_script: 11.5
comp_tokens: 50
N_THREADS:   3
MAX_TOKENS:  50
model_fn:    /mnt/disk2/llamas/TheBloke7B/llama-2-7b.Q4_K_M.gguf
output:      1. everybody has a planet, 2. some planets have moons around them, 3. Pluto is only an object.

### MODEL_NUM: 1 | ITER: 3 ###
time_load:   0.2
time_infer:  3.9
time_script: 4.1
comp_tokens: 11
N_THREADS:   3
MAX_TOKENS:  50
model_fn:    /mnt/disk2/llamas/TheBloke7B/llama-2-7b.Q4_K_M.gguf
output:      1) Mars, 2) Venus and…

### MODEL_NUM: 2 | ITER: 1 ###
time_load:   0.2
time_infer:  16.9
time_script: 17.1
comp_tokens: 50
N_THREADS:   3
MAX_TOKENS:  50
model_fn:    /mnt/disk2/llamas/mistral-7B-v0.1/ggml-model-q4_0.gguf
output:      1) Saturn, 2) Jupiter and 3) Neptune.

### MODEL_NUM: 2 | ITER: 2 ###
time_load:   0.2
time_infer:  16.6
time_script: 16.8
comp_tokens: 50
N_THREADS:   3
MAX_TOKENS:  50
model_fn:    /mnt/disk2/llamas/mistral-7B-v0.1/ggml-model-q4_0.gguf
output:      1. Jupiter, 2. Saturn, 3. Neptune

### MODEL_NUM: 2 | ITER: 3 ###
time_load:   0.1
time_infer:  16.7
time_script: 16.8
comp_tokens: 50
N_THREADS:   3
MAX_TOKENS:  50
model_fn:    /mnt/disk2/llamas/mistral-7B-v0.1/ggml-model-q4_0.gguf
output:      1. Jupiter (88,900 miles in diameter) 2. Saturn (74,600 miles in diameter) 3. Neptune (30,800 miles in diameter)
```