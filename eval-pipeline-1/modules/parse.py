import json
import yaml


def parse(
    text: list, 
    d_md: dict, 
    check_name: bool = False
) -> list:

    parsed_markers = []
    for i, line in enumerate(text):
        for obj, md_header in d_md.items():
            marker = "#" * md_header + " "
            if line.startswith(marker):
                data = line.replace(marker, "").strip()
                if check_name and (data.lower() != obj): continue
                parsed_markers.append((i, obj, data))

    parsed_markers.append((len(text) + 1, None, None)) # include last line

    doc_markers = [
        {
            'start': parsed_markers[i][0] + 1, 
            'end': parsed_markers[i+1][0] - 1, 
            'obj_type': parsed_markers[i][1],
            'obj_name': parsed_markers[i][2],
        }
        for i in range(len(parsed_markers) - 1)
    ]

    return doc_markers


def extract_sections(
    text: list,
    parsed_markers: list,
    compress: bool = False,
) -> list:

    sections = []
    for section in parsed_markers:
        section_text = text[section['start']: section['end']]
        if compress:
            section_text = "".join(section_text)
        sections.append({
            'type': section['obj_type'],
            'name': section['obj_name'],
            'text': section_text
        })
    return sections


def parse_main(
    text: list, 
    md_schema: dict
) -> list:
    
    # parse to major sections
    d_md = {obj: md_schema[obj]['md_header'] for obj in md_schema}

    parsed_markers = parse(text, d_md, check_name=False)

    major_sections = extract_sections(text, parsed_markers)

    output = []
    # parse sub-sections
    for section in major_sections:
        
        section_type = section['type']
        
        d_md = {subsection_name: md_schema[section_type]['children']['md_header']
                for subsection_name in md_schema[section_type]['children']['options']
        }
        
        parsed_markers = parse(section['text'], d_md, check_name=True)
        
        sub_sections = extract_sections(section['text'], parsed_markers, compress=True)

        # parse the meta section
        if section_type == 'meta':
            d_meta = {}
            for line in section['text']:
                try:
                    lines = line.split('\n')
                    k, v = lines.split(':') # TODO - handle multiple colons
                    
                    # TODO - strip bullett lists; but not hyphenated words
                    d_meta[k.strip()] = v.strip()
                except: pass
            sub_sections['meta']['data'] = d_meta
            
        # TODO - handle end character on question text parsing

        output.append({
            'type': section_type,
            'name': section['name'],
            'sub_sections': sub_sections
        })

    return output


def parse_wrapper(
    fn: str  = '../wordle-qa-1/alpha/basic.md',
    md_schema_fn: str = '../wordle-qa-1/alpha/md-schema.yaml',
) -> list:

    with open(fn, 'r') as f:
        text = f.readlines()

    with open(md_schema_fn, 'r') as f:
        md_schema = yaml.safe_load(f)

    return parse_main(text, md_schema)
    
