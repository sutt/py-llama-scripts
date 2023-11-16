#!/bin/bash

output="data/cpp-script-4thread.log"
trials=4
model_fn_1="/mnt/disk2/llamas/TheBloke7B/llama-2-7b.Q4_K_M.gguf"
model_fn_2="/mnt/disk2/llamas/mistral-7B-v0.1/ggml-model-q4_0.gguf"
log_prefix=">>>> "

rm -f $output

for i in $(seq 1 $trials); do

    t0=$(date +%s)
    
    /home/wsutt/llama-cpp/llama.cpp/main \
        -m  $model_fn_1 \
        -p 'Q: What are the three largest planets? A: ' \
        --temp 0.8 \
        -n 50 \
        -t 4 \
        >> $output 2>&1

    
    t1=$(date +%s)
    elapsed=$((t1 - t0))
    
    echo "$log_prefix ### MODEL_NUM: 1 | ITER: $i ###"  >> $output
    echo "$log_prefix time_script: $elapsed" >> $output
    
    echo "script #$i done"
    sleep 1

done

for i in $(seq 1 $trials); do

    t0=$(date +%s)
    
    /home/wsutt/llama-cpp/llama.cpp/main \
        -m  $model_fn_2 \
        -p 'Q: What are the three largest planets? A: ' \
        --temp 0.8 \
        -n 50 \
        -t 4 \
        >> $output 2>&1

    
    t1=$(date +%s)
    elapsed=$((t1 - t0))
    
    echo "$log_prefix ### MODEL_NUM: 2 | ITER: $i ###"  >> $output
    echo "$log_prefix time_script: $elapsed" >> $output
    
    echo "script #$i done"
    sleep 1

done

echo "all scripts done. each output logs appended to $output"

python main.py --summarize $output