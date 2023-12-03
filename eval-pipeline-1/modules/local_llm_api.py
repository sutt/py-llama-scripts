import os
import sys
import ctypes
from llama_cpp import (
    Llama, 
    llama_log_set, 
)

class LocalParams:
    max_tokens = 50
    temperature = 0.8


class LocalModelFns:
    llama_7b = '../../data/llama-2-7b.Q4_K_M.gguf'


def get_model_fn(model_name: str) -> str:
    try:
        return getattr(LocalModelFns, model_name)
    except AttributeError:
        if os.path.isfile(model_name):
            return model_name
        else:
            raise ValueError(f'invalid model_name: {model_name}')
    except Exception as e:
        raise ValueError(f'exception in get_model_fn: {e}')
        

# suppress logs from printing to stdout
# there's still a little that leaks out
def my_log_callback(level, message, user_data): pass
log_callback = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p)(my_log_callback)
llama_log_set(log_callback, ctypes.c_void_p())


class LocalModel:
    def __init__(self, model_name='llama_7b'):
        self.init_params = {
            'n_threads': 4,
        }
        self.generate_params = {
            'temperature': LocalParams.temperature,
            'max_tokens': LocalParams.max_tokens,
        }
        self.llm = Llama(
            model_path=get_model_fn(model_name), 
            **self.init_params,
        )

    def __call__(self, prompt):
        output = self.llm(
            prompt=prompt, 
            **self.generate_params,
        )
        return output
    
    @staticmethod
    def get_completion(output):
        return output['choices'][0]['text']
    
    @staticmethod
    def get_data(output):
        data = {
            'text': output['choices'][0]['text'],
            'completion_tokens': output['usage']['completion_tokens'],
        }
        return data


if __name__ == '__main__':
    
    print("start...\n")
    local_model = LocalModel('llama_7b')
    prompt = 'Q: What is the largest planet? A: '
    output = local_model(prompt)
    print(output)
    text = LocalModel.get_completion(output)
    print(text)
    print("\nend.")

