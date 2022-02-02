import argparse
import sys
import yaml
from collections import defaultdict
from os import path, walk
from xml.dom import minidom
from yaml.representer import Representer
yaml.add_representer(defaultdict, Representer.represent_dict)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    args = parse_args(args)

    baseline_path = path.join(args.rootpath, 'baseline')
    complements_path = path.join(args.rootpath, 'complements')
    data_outpath = path.join(args.rootpath,'data/data.yml')

    svgs = generate_structured_data(baseline_path)
    svgs['complements'] = generate_structured_data(complements_path)

    save_yaml(svgs, data_outpath)
    print(f'Extracted data file saved in: {data_outpath}')

def generate_structured_data(rootpath: str) -> defaultdict:
    """
    Iterate over a folder extracting elements (using extract_elements function)
    from the files maintaining the hierarchy of the file structure translating to 
    a defaultdict object

    Args:
        rootpath (str): path where to extract all elements recursively

    Returns:
        defaultdict: Dictionary of dictionaries mantaining file structure hierarchy
    """    
    svgs = defaultdict(list)
    for root, _, files in walk(rootpath):
        if files:
            key = path.basename(root)
            svgs[key] = {f.split('.')[0]: extract_elements(path.join(root, f)) for f in files if f != '.gitignore'}
            for s in svgs[key]: svgs[key][s]['priority'] = 0
    return svgs

def extract_elements(filepath: str) -> dict:
    """
    Given a filepath, obtain id and d elements from parsed xml tags (<path/>).
    The 'path' tag looks like this:
    
        <path id="color_3" class="cls-4" d="M1435,559c12.61,0.453,27.33,24"/>

        - id : identifier of the tag
        - d  : SVG vector / drawing

    Args:
        filepath (str): svg file path

    Returns:
        dict: dictionary with id as keys and d as values
    """    
    doc = minidom.parse(filepath)
    path_id = [path.getAttribute('id') for path
                    in doc.getElementsByTagName('path')]
    path_strings = [path.getAttribute('d') for path
                    in doc.getElementsByTagName('path')]
    elements = {id:strings for id, strings in zip(path_id, path_strings)}
    return elements

def save_yaml(svgs: defaultdict, output_path: str) -> None:
    """
    Save a defaultdict object as yml file in output directory

    Args:
        svgs (defaultdict): structured data in dictionary form
        output_path (str): path where the .yml file is saved
    """    
    with open(output_path, 'w') as of:
        yaml.dump(svgs, of, default_flow_style=False)

def parse_args(args):
    description = '''
    Extract svg vector data from svg files stored in baseline and complements folders and create data.yml file in data folder.
    '''
    epilog = '''
            python3 ./disunaurio_nft/data_extractor.py
    '''
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=epilog
    )
    parser.add_argument('--rootpath', default=path.join(path.realpath('.'),'svg_files'), help='')
    return parser.parse_args(args)

if __name__ == '__main__':
    main()
