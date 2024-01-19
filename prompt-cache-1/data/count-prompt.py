import sys
sys.path.append('..')
from utils import tokenize_text

model_path = '../../../../../data/mistral-7b-instruct-v0.2.Q4_K_M.gguf'

text_fn = sys.argv[1]

text = open(text_fn).read()

tokens = tokenize_text(model_path, text)
    
print(f'n_tokens: {len(tokens)}')
