import json
import time
import io
import ctypes
from contextlib import redirect_stderr
from llama_cpp import (
    Llama,
    llama_log_set,
)
from collections import OrderedDict
from typing import (
    Dict,
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

def reverse_cumsum(d: OrderedDict) -> dict:
    '''
        {a:1,b:3,c:10} -> {a:1,b:2,c:7}
    '''
    tmp = [(k,v) for k,v in d.items()]
    d = OrderedDict(**{tmp[0][0]:tmp[0][1]})
    for i, e in enumerate(tmp[1:]):
        d[e[0]] = e[1] - tmp[i][1]
    return d


def get_llm_stats(llm: Llama) -> dict:
    num_tokens = llm.n_tokens
    return {
        'num_tokens': num_tokens,
    }

class ProfileStats:
    def __init__(self, name:str=None):
        self.name = name
        self.d_info = OrderedDict()
        self.t0 = time.time()
    def add(self, 
            key:str,
            num_tokens:int=None,
            llm:Llama=None,
        ) -> None:
        '''
            log `time` to `key` of current time against time of init
            optionally: add `num_tokens` and/or Llama object attrs
        '''
        stats_kv = {}
        if llm is not None:
            stats_kv = get_llm_stats(llm)
        if num_tokens is not None:
            stats_kv['num_tokens'] = num_tokens
        self.d_info[key] = {
            'time': time.time() - self.t0,
            **stats_kv
        }
        return
    def get(self) -> Dict[str, Dict[str, float]]:
        return self.d_info
    def calc(self) -> Dict[str, Dict[str, float]]:
        '''
            compute extra stats from raw data
        '''
        # transform time: currently cumulative, list as elapsed between ordered points
        d_time      = {k: v.get('time') for k,v in self.d_info.items()}
        d_time      = reverse_cumsum(d_time)
        # apply transforms on stats
        d_tokens    = {k: v.get('num_tokens') for k,v in self.d_info.items()}
        d_tps       = {k: v.get('num_tokens') / v.get('time') 
                       for k,v in self.d_info.items()
                       if v.get('num_tokens') is not None and v.get('time') is not None
                       }
        # combine them: d_time[k] always present, d_tokens[k] is not
        d_info = {
            k : {
                'time': d_time.get(k),
                'num_tokens': d_tokens.get(k),
                'tps': d_tps.get(k),
                }
            for k in d_time.keys()
        }
        return d_info
    def fmt_json(self, round_places:int=2):
        data = self.calc()
        data = {k: format(v, f'.{round_places}f') for k,v in data.items()}
        return json.dumps(data, indent=2)
    def fmt_grid(self, round_places:int=2, n_chars:int=13) -> str:
        '''
            print formatted table
        '''
        data = self.calc()
        header = ['key', 'time', 'num_tokens', 'tps']
        header = ''.join('{:<{n_chars}}'.format(e, n_chars=n_chars) for e in header)
        table = [header]
        for k in data.keys():
            row = '{:<{n_chars}}'.format(k, n_chars=n_chars)
            for k_stat, v_stat in data[k].items():
                fmt_stat = 'n/a' if v_stat is None else format(v_stat, f'.{round_places}f')
                row += '{:<{n_chars}}'.format(fmt_stat, n_chars=n_chars)
            table.append(row)
        table = '\n'.join(table)
        return table
            
        
    
if __name__ == '__main__':

    print('testing ProfileStats')
    
    ps = ProfileStats('func1')
    ps.add('point1')
    time.sleep(.1)
    ps.add('point2', num_tokens=10)
    time.sleep(.2)
    ps.add('point3', num_tokens=20)

    data = ps.get()
    print(json.dumps(data, indent=2))
    data2 = ps.calc()
    print(json.dumps(data2, indent=2))
    fmt_data = ps.fmt_grid()
    print(fmt_data)

