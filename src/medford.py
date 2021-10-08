from medford_detailparser import *
from medford_detail import *
from medford_models import BCODMO, Entity
from functools import reduce 
from helpers_file import swap_file_loc
from medford_BagIt import runBagitMode, BagIt
import json

import argparse

from enum import Enum, auto


class MFDMode(Enum) :
    OTHER = 'OTHER'
    BCODMO = 'BCODMO'
    BAGIT = 'BAGIT'

    def __str__(self):
        return self.value

class ParserMode(Enum) :
    validate = 'validate'
    compile = 'compile'

    def __str__(self):
        return self.value
    
# Command Line Arguments
# TODO: How can I make it require an MFDMode value, but lowercase is OK?
#       Do I actually care?
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--mode", type=MFDMode, choices=list(MFDMode), default=MFDMode.OTHER, required=True,
    help="Which Output mode the MEDFORD parser should validate or compile for.")
parser.add_argument("action", type=ParserMode, choices=list(ParserMode), 
    help="Whether the MEDFORD parser is only validating or actually compiling (performing any necessary adjustments or actions for the appropriate format, such as creating a Bag for the BagIt mode.)")
parser.add_argument("file", type=str, help="The input MEDFORD file to validate or compile.")
parser.add_argument("--write_json", action="store_true", default=False,
    help="Write a JSON file of the internal representation of the MEDFORD file beside the input MEDFORD file.")
parser.add_argument("--debug", "-d", "-v", action="store_true", default=False,
    help="Enable verbose mode for MEDFORD, enabling various debug messages during runtime.")

def runMedford(filename, output_json, mode):
    class FieldError(Exception):
        pass

    details = []
    with open(filename, 'r') as f:
        all_lines = f.readlines()
        prev_detail = None
        for i, line in enumerate(all_lines):
            if(line.strip() != "") :
                noncomment, new_detail, returned_detail = detail.FromLine(line, i+1, prev_detail = prev_detail)
                if noncomment and new_detail :
                    details.append(returned_detail)
                if noncomment:
                    prev_detail = details[-1]

    parser = detailparser(details)
    final_dict = parser.export()
    if mode == MFDMode.BCODMO:
        p = BCODMO(**final_dict)
    elif mode == MFDMode.BAGIT:
        p = BagIt(**final_dict)
        # Iterate through all Files and:
        #   - create hash
        #   - copy to new subdir & location in data/
        runBagitMode(p, filename)
    elif mode == MFDMode.OTHER:
        p = Entity(**final_dict)
    else :
        raise Exception("Medford is running in an unsupported mode.")

    if(output_json) :
        with open(filename + ".JSON", 'w') as f:
            json.dump(final_dict, f, indent=2)

if __name__ == "__main__":
    args = parser.parse_args()

    runMedford(args.file, args.write_json, args.mode)