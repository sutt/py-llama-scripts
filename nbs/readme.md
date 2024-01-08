## Notebooks for Explorations

### [load-state-xxx.ipynb]
 - "caching prompt" saving/loading state from a prompt
 - currently on llama-cpp-python v0.2.26
 - [./load-state-b.ipynb](./load-state-b.ipynb) 
    - using example from: https://github.com/abetlen/llama-cpp-python/issues/997
    - this has two prompts (about different fictional character backgrounds) saved that should produce different results when asked the same question
  -[./load-state-c.ipynb](./load-state-c.ipynb)
    - this uses one large prompt to ask two questions of it.
    - we use the large prompt to accentuate the prompt eval time
    - we using timing dictionaries to profile execution time
- [load-state-1.ipynb] - first unsuccesful attempt at this
    - could be because I was an older version (~v0.2.19)

### [more-ctx-1.ipynb](./more-ctx-1.ipynb)
  - how to increase the context window to accomodate large prompt
  
### [book2.ipynb](./book2.ipynb)
 - suppressing stdout output
 - tokenization

### [book3.ipynb](./book3.ipynb)
 - logprob output

### [book4.ipynb](./book4.ipynb)
 - using OpenAI API

### [book5.ipynb](./book5.ipynb)
 - parsing question markdowns to json




