import os, sys, time, json, argparse
import uuid
from typing import Union
from modules.parse import parse_wrapper
from modules.oai_api import submit_prompt, get_completion
from modules.output import output_json, output_markdown

def main(
    input_md_fn: str,
    input_schema_fn: str,  # TODO - add default schema
    output_md_fn: Union[None, str] = None,
    output_json_fn: Union[None, str] = None,
    tic: Union[None, float] = None,
) -> list:
    
    json_doc = parse_wrapper(
        fn=input_md_fn,
        md_schema_fn=input_schema_fn,
    )
    
    output = []
    for question in [e for e in json_doc if e['type'] == 'question']:
        try:
            name = question['name']
            question = [e for e in question['sub_sections'] if e['type'] == 'question'][0]['text']
        except Exception as e:
            print(e)
            continue
        answer = None 
        error = None
    
        try:
            completion = submit_prompt(
                prompt=question,
                model_name="gpt-3.5-turbo",  # TODO - this is at level of main
                max_tokens=200,  # TODO - use question-specific max_tokens
                temperature=0.7,
            )
            answer = get_completion(completion)
        except Exception as e:
            error = e
        
        output.append({
            'name': name,
            'question': question,
            'answer': answer,
            'error': error,
            # TODO - add model name
            # TODO - add timestamp
        })
        
        if tic is not None:
            time.sleep(tic)

    if output_json_fn is not None:
        output_json(output_json_fn, output)
    
    if output_md_fn is not None:
        output_markdown(output_md_fn, output)

    return output    


if __name__ == '__main__':
    input_md_fn = '../wordle-qa-1/alpha/basic.md'
    input_schema_fn = '../wordle-qa-1/alpha/md-schema.yaml'
    output_md_fn = '../wordle-qa-1/alpha/output1.md'
    # output_json_fn = '../wordle-qa-1/alpha/output1.json'
    output_json_fn = None
    tic =  1.0
    main(
        input_md_fn=input_md_fn,
        input_schema_fn=input_schema_fn,
        output_md_fn=output_md_fn,
        output_json_fn=output_json_fn,
        tic=tic,
    )
    print('done')
