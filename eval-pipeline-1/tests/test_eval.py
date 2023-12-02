import os, sys, json, time
from unittest import mock
sys.path.append('../')

from main import eval_sheet
from modules.oai_api import get_completion
from openai.types.chat import ChatCompletion

def load_chat_completion(fn: str) -> ChatCompletion:
    '''need this since oai_api.get_completion takes a ChatCompletion object'''
    with open(fn, 'r') as f:
        data = json.load(f)
        return ChatCompletion(**data)
    
RESPONSE_STUB_FN = './data/stubs/completion.json'
MODEL_RESPONSE_STUB = load_chat_completion(RESPONSE_STUB_FN)

def test_stub_loaded():
    '''test to make sure subsequent tests are valid'''
    msg = get_completion(MODEL_RESPONSE_STUB)
    assert len(msg) > 0


def test_eval_basic_1():
    '''
        demonstrate mocking:
         - output file(s): .md + .json
         - submit_prompt
    '''
    
    with mock.patch('modules.output.open',  mock.mock_open()) as mock_output_file:
        with mock.patch('main.submit_prompt') as mock_submit_prompt:
            
            mock_submit_prompt.return_value = MODEL_RESPONSE_STUB
            
            output = eval_sheet(
                './data/input-one.md',
                '../data/md-schema.yaml',
                'gpt-3.5-turbo',
                'should-not-be-used.txt',
                verbose_level=0,
            )

            mock_submit_prompt.call_count == 2
    
            written_data = [e[0][0] for e in mock_output_file().write.call_args_list]
            
            assert len(written_data) > 0
            

# TODO - test the json output
# TODO - better test of markdown output