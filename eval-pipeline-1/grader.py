import json
import argparse
from modules.parse import parse_wrapper
from main import grade_sheet

def do_grade_sheet(
        input_md_fn: str,
        input_schema_fn: str,
        output_json_fn: str,
        grade_json_fn: str = None,
        verbose: bool = False,
):
    json_doc = parse_wrapper(
        fn=input_md_fn,
        md_schema_fn=input_schema_fn,
    )

    with open(output_json_fn, 'r') as f:
        output_obj = json.loads(f.read())

    grades = grade_sheet(
        json_doc=json_doc,
        output_obj=output_obj,
    )

    if verbose:
        print(grades)

    if grade_json_fn is not None:
        with open(grade_json_fn, 'w') as f:
            json.dump(grades, f, indent=2)
    
    return grades

if __name__ == '__main__':

    argparser = argparse.ArgumentParser()
    argparser.add_argument('-i', '--input_fn',      type=str)
    argparser.add_argument('-s', '--schema_fn',     type=str)
    argparser.add_argument('-o', '--output_fn',     type=str)
    argparser.add_argument('-g', '--grade_fn',      type=str)
    argparser.add_argument('-v', '--verbose',       action='store_true')
    args = argparser.parse_args()
    args = vars(args)
    
    # set defaults
    input_md_fn='../wordle-qa-1/delta/input-basic.md'
    input_schema_fn='data/md-schema.yaml'
    # output_json_fn='../wordle-qa-1/beta/output-basic-gpt-4-84b4.json'
    output_json_fn='../wordle-qa-1/beta/output-basic-gpt-3.5-turbo-90f5.json'
    grade_json_fn = None
    verbose = False

    if args['input_fn'] is not None:
        input_md_fn = args['input_fn']
    if args['schema_fn'] is not None:
        input_schema_fn = args['schema_fn']
    if args['output_fn'] is not None:
        output_json_fn = args['output_fn']
    if args['grade_fn'] is not None:
        grade_json_fn = args['grade_fn']
    if args['verbose'] is not None:
        verbose = args['verbose']

    grades = do_grade_sheet(
        input_md_fn=input_md_fn,
        input_schema_fn=input_schema_fn,
        output_json_fn=output_json_fn,
        verbose=verbose,
        grade_json_fn=grade_json_fn,
    )