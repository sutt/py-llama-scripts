import json

def output_json(output_fn, output):
    with open(output_fn, 'w') as f:
        json.dump(output, f, indent=2)

def output_markdown(output_fn, output):
    with open(output_fn, 'w') as f:
        for e in output:
            name = e['name']
            question = e['question']
            answer = e['answer']
            error = e['error']
            f.write(f'### {name}\n')
            f.write(f'**Question:**\n{question}\n')
            if error is not None:
                f.write(f'**Error:**\n{error}\n')
            else:
                f.write(f'**Answer:**\n{answer}\n')
            f.write('\n')
