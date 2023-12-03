import os, sys, json, time
from unittest import mock
sys.path.append('../')

from main import eval_sheet
from modules.oai_api import get_completion
from modules.local_llm_api import get_model_fn
from openai.types.chat import ChatCompletion

def load_chat_completion(fn: str) -> ChatCompletion:
    '''need this since oai_api.get_completion takes a ChatCompletion object'''
    with open(fn, 'r') as f:
        data = json.load(f)
        return ChatCompletion(**data)
    
RESPONSE_STUB_FN = './data/stubs/completion.json'
MODEL_RESPONSE_STUB = load_chat_completion(RESPONSE_STUB_FN)

VALID_MODEL_PATH = '../../../data/llama-2-7b.Q4_K_M.gguf'


def test_stub_loaded():
    '''test to make sure subsequent tests are valid'''
    msg = get_completion(MODEL_RESPONSE_STUB)
    assert len(msg) > 0


def test_get_model_fn():
    # valid model_name should return a path
    model_fn = get_model_fn('llama_7b')
    assert model_fn == '../../data/llama-2-7b.Q4_K_M.gguf'
    # valid path to a file should return the path
    model_fn = get_model_fn(VALID_MODEL_PATH)
    assert model_fn == VALID_MODEL_PATH
    # invalid model_name should raise ValueError
    try:
        model_fn = get_model_fn('llama_7b_fake')
        assert False
    except ValueError:
        assert True
    except:
        assert False


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

            # two questions thus it should be called twice
            mock_submit_prompt.call_count == 2
    
            # verify the output file is written to, but not much else
            written_data = [e[0][0] for e in mock_output_file().write.call_args_list]
            
            assert len(written_data) > 0


def test_eval_basic_2():
    '''
        test with local model: llama_7b
    '''
    
    with mock.patch('modules.output.open',  mock.mock_open()) as mock_output_file:
        with mock.patch('main.prompt_model') as mock_prompt_model:
            
            mock_prompt_model.return_value = ("stubbed answer", None)
            
            output = eval_sheet(
                './data/input-one.md',
                '../data/md-schema.yaml',
                'llama_7b',
                'should-not-be-used.txt',
                verbose_level=0,
            )

            # two questions thus it should be called twice
            mock_prompt_model.call_count == 2
    
            # verify the output file is written to, but not much else
            written_data = [e[0][0] for e in mock_output_file().write.call_args_list]
            
            assert len(written_data) > 0
            

# TODO - test the json output
# TODO - better test of markdown output