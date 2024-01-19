# Prompt Caching Demonstration App

Prompt caching is a technique for speeding up the completion of a prompt by caching the results of previous completions. This is a demonstration app for the technique.

**At a broad level,** prompt-caching is saving the state of the language models activations at a checkpoint - usually after the system prompt and before the user prompt. This resetting of state is a lot quicker than evaluating the full system prompt and thus inference is quicker. This is useful for getting near real-time conversation speeds with a relatively simple inference system.

For example, let's say you have two different restuarants A and B that you are serving chatbots for. In the prompt you can include all information relevant to each of these restaurants and save that state.

Or you could have a micro-service pipeline of NLP services that are specialized via an engineered prompt.

### Benchmarking

The script will printout logs of the time taken to complete each step of the prompt.

As can be seen the `eval_prompt` is about two orders of magnitude faster than the `main_sample` step. This is because the prompt caching of the original `eval_time` in the save_state step.

See [output](./output/) directory for more examples. These were created with a low-perf / no-gpu machine, but the relative times should scale up with better hardware.


```
#### Starting FAA example (mistral-hf formatted):
Estimated ~31 secs to cache prompt ...

key          time         num_tokens   tps          
reset        0.00         n/a          n/a          
eval_time    21.13        186.00       8.80         
save_state   0.08         n/a          n/a          

### Saved Cache State
## Question 0: 
Question: What was the destination of the plane? [/INST]
# Trial 0:
 The destination of the plane was Ontario, California.

key          time         num_tokens   tps          
load_state   0.04         n/a          n/a          
eval_prompt  1.83         203.00       108.64       
main_sample  1.40         10.00        3.06      
```

#### Misc Brainstorming:

 - Prompt-caching is somewhere in between RAG and fine-tuning:
    - Like RAG, it uses extra information outside the user's message.
    - Like fine-tuning, it helps the model perform in a customized way.
    - But, it has the pro that it doesn't require the training epochs which are costly, create iteration lag, and require data. Instead the updated inference model is available immediately after saving the state which takes ~20 secs.

  - NLP microservices pipelines:
    - example: a) extract all employers b) normalize each employer candidate to a canonical form.

  - How could you generate arbitrary evals? Something like generating different queries automatically and asking different models to produce an answer, or different seeds and see if there's any discrepencies on this. Produce a an implication question, e.g. since we're out of cheese pizza i should not add this an item to any orders, correct? is this jsut today or forever? etc.

  - You could fine-tune in abbreviations and reasoning agents e.g. ItemLookup(exactMatch) but in minifed-javascript form. 

### Todos

```markdown
[x] remove the initial printout
[x] print the multiple times
[x] explain why the thing stopped
    -> it didn't but the following completion took all the tokens
    \end{blockquote}
    -> fixed via replace the apostophes in the quoted article
[x] different seed, temp
[x] separate into more modules
[x] better/DRYer time-logging
[x] add typing
[x] add random/setseed
[x] add mini example
    - e.g. "the mouse was named Dave" "Q: what is mouse's name?"
[x] add line carriage between completion and 
[x] move prompt into data directory
[x] refactor askTheQuestion / createState
[X] refactor out stderr_redirect from main
[x] refactor as much of llama_log_set boilerplate from main as possible
[x] get an insturct model working
[x] add versioning info in workspace
[x] install new version in beta-app
    -> py_llama: 2.19 -> 2.29
    [x] can you run jupyter-nb without installing the package -> no
[x] quick test of the prompt-cache-1/main.py (wired to alpha-app/data)

[x] add an instruct model locally

    [x] make this mistral-7b-instruct
        https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
        mistral-7b-instruct-v0.2.Q4_K_M.gguf
        [x] get mistral to work on server
            [x] download v2 model  
            - run on mnt/disk2/hg-client/client.py (after settings vars)
            [x] succesful instruct
            -> in llama.cpp/ >./sut-mistral-1.sh
            -> /mnt/disk2/llamas/MistralBlokeHF/mistral-7b-instruct-v0.2.Q4_K_M.gguf
            -><s>[INST] List five words which are associated with the study of Geology. [/INST]

    [x] download the model -> llms/data/
    [x] run locally in notebook on py_llama_cpp

    [x] add to prompt-cache-1
    
[x] move models: llms/pkgs/alpha-app/data/ -> llms/data/
[x] create output with mistral-instruct
[x] move around readme's

[x] add llm stats / token length stats to ProfileStats
    - completion time depends on length
[x] refactor main() -> one_prompt_multi_questions()
[~] json print rounded floats
[x] add new method multi_prompt_multi_questions() example
[x] add utility to tokenize the prompt
[x] expand the prompt/question eval framework

[x] add write save_state to disk
    - what is r/w perf on this?
[ ] add the updating of current information

[ ] full json mode
    - refactor `verbose` to streaming real-time mode
    - add full_log class (defined in utils) which is called main helper functions

[ ] compare benchamrks of 
    - 0.2.19 vs 0.2.26
    - llama7b vs mistral7b
    - local windows vs remote linux

Future links:
    Mistral demonstration notebook
    https://colab.research.google.com/drive/1F2PeWl5FOHv4sjd7XTEu40JjqbFhC3LB?usp=sharing

    ChatTemplates - the problem(?) with OpenOrca
    https://huggingface.co/docs/transformers/main/chat_templating

    Mistral readme.md
    https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2


```
### Thoughts:

