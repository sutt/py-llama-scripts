import sys
sys.path.append('../')
import os, json, time
from modules.parse import parse_wrapper
from main import collect_input_sheets

def test_1():
    assert True

def test_section_parse_1():

    doc_obj = parse_wrapper(
        './data/input-one.md',
        '../data/md-schema.yaml',
    )
    print(json.dumps(doc_obj, indent=2))
    # assert False
        
    questions = [e for e in doc_obj if e['type'] == 'question']
    sheets = [e for e in doc_obj if e['type'] == 'sheet']
    q0_text = [e for e in questions[0]['sub_sections'] if e['type'] == 'question'][0]['text']
    q1_subsection_types = [e['type'] for e in questions[1]['sub_sections']]

    Q0_TEXT = "Q: What did the early bird get?\nA:\n"

    assert len(questions) == 2
    assert len(sheets) == 1

    assert questions[0]['name'] == 'Question-One-1'

    assert q0_text == Q0_TEXT

    assert len(q1_subsection_types) == 2
    assert len([e for e in q1_subsection_types if e in ('meta', 'question')])


def test_meta_kv_parse_1():
    
    doc_obj = parse_wrapper(
        './data/input-one.md',
        '../data/md-schema.yaml',
    )
    
    def get_meta_data(question_obj):
        return [e for e in question_obj['sub_sections'] if e['type'] == 'meta'][0]['data']
    
    questions = [e for e in doc_obj if e['type'] == 'question']
    q0_meta = get_meta_data(questions[0])
    q1_meta = get_meta_data(questions[1])

    assert q0_meta.get('answer_suggested_length') == "50"
    assert q1_meta.get('answer_suggested_length') == "22"
    assert q0_meta.get('answer_type') == "multiple-choice"
    

def test_last_char_parse_1():
    pass


def test_collect_input_sheets_1():
    
    sheets_dir = './data/dir-one'

    input_sheets = collect_input_sheets(
        sheets_dir=sheets_dir,
    )
    
    assert len(input_sheets) == 2
    assert './data/dir-one/input-two.md' in input_sheets
    assert './data/dir-one/input-one.md' in input_sheets