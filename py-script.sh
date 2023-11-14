#!/bin/bash

output="data/time-script-demo.log"
trials=2

rm -f $output

for i in $(seq 1 $trials); do
    python main.py --model_num 1 --iter_num $i >> $output 2>&1
    echo "script #$i done"
    sleep 1
done

for i in $(seq 1 $trials); do
    python main.py --model_num 2 --iter_num $i >> $output 2>&1
    echo "script #$i done"
    sleep 1
done

echo "all scripts done. each output logs appended to $output"

python main.py --summarize $output



