import ctypes
import json
from llama_cpp import llama_log_set
from llama_cpp import Llama

num_logprobs =  10
max_tokens =    2
fn = 'logprobs-1.json'

# prompt = '''He opened up the door and saw a woman and her eyes were'''
prompt = '''She was the most beautiful woman in the world. Her hair was red and her eyes were'''

def my_log_callback(level, message, user_data):
    pass
log_callback = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p)(my_log_callback)
llama_log_set(log_callback, ctypes.c_void_p())

model_fn = '/mnt/disk2/llamas/TheBloke7B/llama-2-7b.Q4_K_M.gguf'
llm = Llama(
    model_fn, 
    logits_all=True
)

model_params = {
    'temperature': 0.8,
    'max_tokens': max_tokens,
}

print("starting the completion...")
output = llm(
    prompt=prompt, 
    logprobs=num_logprobs, 
    **model_params,
)

with open(fn, 'w') as f:
    print(f"outputting to {fn}")
    json.dump(output, f, indent=2)