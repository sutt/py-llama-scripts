import json
'''
    generate a json file of the output type
    expected of the main app.
    using the .txt file of your prompt. 
    this handles encoding a multi-line doc
'''

prompt_questions_model = {
    'prompt': '',
    'questions': [],
}

# change these variables, including
input_fn = './faa.txt'
output_fn = './faa-mistral.json'
questions = [
    '''\nQuestion: What was the destination of the plane? [/INST]''',
    '''\nQuestion: What was the origin of the plane? [/INST]''',
]

with open (input_fn, 'r') as f:
    prompt_questions_model['prompt'] = f.read()

prompt_questions_model['questions'] = questions

with open (output_fn, 'w') as f:
    json.dump(prompt_questions_model, f, indent=2)