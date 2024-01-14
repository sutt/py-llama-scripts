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
output_fn = './faa.json'
questions = [
    '''What was the destination of the plane? Answer:''',
    '''What was the origin of the plane? Answer:''',
]

with open (input_fn, 'r') as f:
    prompt_questions_model['prompt'] = f.read()

prompt_questions_model['questions'] = questions

with open (output_fn, 'w') as f:
    json.dump(prompt_questions_model, f, indent=2)