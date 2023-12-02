import json

# TODO - add eval_time to details
# TODO - add answer to details

def wrap_md_detail(output):
    return f'''
<details>
<summary>meta_data:</summary>

{output}

</details>
'''


def format_meta_data(meta_data, md_detail=True):
    output = ''
    for k, v in meta_data.items():
        output += f'- {k}: {v}\n'
    if md_detail:
        output = wrap_md_detail(output)
    return output


def output_json(output_fn: str, output: dict):
    with open(output_fn, 'w') as f:
        json.dump(output, f, indent=2)


def output_markdown(output_fn: str, output: dict):
    
    with open(output_fn, 'w') as f:
        
        sheet = output.get('sheet')
        if sheet is not None:
            sheet_name = sheet.get('name')
            run_id = sheet.get('run_id')
            f.write(f'# {sheet_name}\n')
            f.write(f'**Run ID:** {run_id}\n')

        for e in output['questions']:
            
            name = e.get('name')
            model_name = e.get('model_name')
            question = e.get('question')
            answer = e.get('answer')
            error = e.get('error')
            meta_data = e.get('meta_data')

            f.write(f'### {name}\n')

            if meta_data is not None:
                f.write(f'**Meta Data:**\n{format_meta_data(meta_data)}\n')
            
            f.write(f'**Model:**\n{model_name}\n')
            
            f.write(f'**Question:**\n{question}\n')
            
            if error is not None:
                f.write(f'**Error:**\n{error}\n')
            
            else:
                f.write(f'**Answer:**\n{answer}\n')
            
            f.write('\n')


if __name__ == '__main__':
    out = format_meta_data({'a': 1, 'b': 2}, md_detail=False)
    print(out)