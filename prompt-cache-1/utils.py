import json
import time
import io
import ctypes
from contextlib import redirect_stderr
from llama_cpp import (
    Llama,
    llama_log_set,
)

# suppressing + logging stdout/stderr -----

llama_log_obj = []

def suppress_stderr(func):
    def wrapper(*args, **kwargs):
        capture_stderr = io.StringIO()
        with redirect_stderr(capture_stderr):
            result = func(*args, **kwargs)
            llama_log_obj.append(capture_stderr.getvalue())
        return result
    return wrapper

def my_log_callback(level, message, user_data):
    llama_log_obj.append(message.decode())

log_callback = ctypes.CFUNCTYPE(None, ctypes.c_int, 
            ctypes.c_char_p, ctypes.c_void_p)(my_log_callback)

llama_log_set(log_callback, ctypes.c_void_p())

# misc ------

@suppress_stderr
def tokenize_text(model_path, text):
    llm = Llama(
        model_path,
        vocab_only=True,
        )
    tokens = llm.tokenize(text.encode())
    return tokens

# profiling utilities -----

def reverse_cumsum(d):
    tmp = [(k,v) for k,v in d.items()]
    d = {tmp[0][0]:tmp[0][1]}
    for i, e in enumerate(tmp[1:]):
        d[e[0]] = e[1] - tmp[i][1]
    return d

# def get_llm_stats(llm, big_text):
#     num_tokens = len(llm.tokenize( big_text.encode()))
#     llm_n_ctx = llm.n_ctx()
#     llm_n_tokens = llm.n_tokens
#     json_stats = json.dumps({
#         'num_tokens': num_tokens,
#         'llm_n_ctx': llm_n_ctx,
#         'llm_n_tokens': llm_n_tokens,
#     }, indent=2)
#     return json_stats

class ProfileStats:
    def __init__(self):
        self.d_time = {}
        self.t0 = time.time()
    def add(self, key):
        self.d_time[key] = time.time() - self.t0
    def dumps(self):
        return json.dumps(
            self._round_values(
                reverse_cumsum(self.d_time)
                ), indent=2
        )
    def _round_values(self, d, n_places=2):
        # TODO - find a way to output as float not string
        return {k:format(v, f'.{n_places}f') for k,v in d.items()}