import ctypes
from llama_cpp import llama_log_set 

def suppress_output():
    def my_log_callback(level, message, user_data):
        pass
    log_callback = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p)(my_log_callback)
    llama_log_set(log_callback, ctypes.c_void_p())
