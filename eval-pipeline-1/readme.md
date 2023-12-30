# LIME - Eval-Pipeline

A homebrewed Language Model Eval tool.  Specifically a cli pipeline to:
 - Parse question/answer datasets in markdown format:
 - Evaluate the language models on these datasets:
    - process these datasets into openai api and locally deployed llamas models
    - automatically grade the results
 - Aggregate / summarize / compare the results.

This was built on a [dataset](https://github.com/sutt/wordle-qa-2) which uses different questions about playing the game wordle, essentially asking the language model to parse commands in both NLP and semi-structured formats (e.g. JSON representation)

TODO - insert a diagram

### Script Tools

There are three main actions that can be taken with this tool:

 - `main.py`: run a specified model on a sheet, create an output
 - `grader.py`: update the grading and ground_truth of a sheet
 - `agg.py`: aggregate and compare the results of multiple model runs

Run the bash scripts in the `scripts/` directory from repo root (and supplementary windows batch files) as they require multiple arguments with path and filename specification.

##### Run Models on Question Sheets - `./scripts/main.sh`:
```bash
python main.py \
   -f ../wordle-qa-2/what-shows-up/input-wsu-1.md \  #input-sheet
   # -d ../wordle-qa-2/what-shows-up \  # input-directory
   -m gpt-4 \   # model name
   -u 4 \  # number of uuid chars to generate
   -j \    # json output
   -v \  # verbose 
```
Run a specified model on a specified sheet (or directory of sheets) and create an output file in the directory of the input sheet. If a directory is specified as an input one, outputs file per input-sheet) and applies grading after processing the models.

Can use `collect_results.sh` script here to move all output files into a single directory for aggregation.

```bash
destination_dir="_results"
mkdir -p "$destination_dir"
find . -type f -name "output*" -exec mv {} "$destination_dir" \;
find . -type f -name "grade*" -exec mv {} "$destination_dir" \;

```

##### (Re)grade the output of a model run - `./scripts/grader.sh`:
```bash
python grader.py \
   -o ../wordle-qa-2/results/output-wsu-1-gpt-3.5-turbo-4bd8.json \ # output file to grade/overwrite
   -i ../wordle-qa-2/what-shows-up/input-wsu-1.md \  # optional input file
   -v \   # verbose
   -w \   # write changes; leave off for dry run
   -l \   # "liberal grading" option
```

Take as input (`-o`) an output file for update the grading field of each question there in. Optionaly, if specified with an input file to an input-sheet (`-i`) can update the ground_truth field of questions, when ground_truth is initially ill-specifed or needs to be updated.

##### Aggregate and Compare Model Runs - `./scripts/agg.sh`:

```bash
python agg.py \
   -i ../wordle-qa-2/results \
   -v 
#  -o ../wordle-qa-2/results/agg-mysummary-1.md
```

Generated summary tables of aggregation and comparison for all all output-*.json files found in the supplied input directory. Outputs this data as markdown format (from pandas) into an `agg-xxxx.md` file in the input directory (4 char uuid by default unless output filepath `-o` flag is specified).



### Outputs

### Quicklaunch

```bash

```

### Explanations

#### Markdown Questions

Tradeoffs we're looking to hit:
- accessible to no-code users
- ease of version control diffing + cli tools
    - no html, no database
- good enough control over formatting, whitespace, unicode, etc
- allows semi-structured format

This uses markdowns as compromise between the ease of editing and the flexibility of json/yaml. 
- **MdSchema**:  `md-schema.yaml`.

Explain the cascading system_prompt, meta settings

Using \<EVAL-ENDCHAR\> / |EVAL-ENDCHAR| tokens

### Results

TODO - insert the tables from agg results here
