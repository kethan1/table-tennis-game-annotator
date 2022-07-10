import os
import json
import argparse


parser = argparse.ArgumentParser()
parser.add_argument(
    "--annotation-file1",
    help="path to annotation file 1",
    default="",
)
parser.add_argument(
    "--annotation-file2",
    help="path to annotation file 2",
    default="",
)
parser.add_argument(
    "--output-annotation",
    help="path to a the output annotation file",
    default="",
)

args = parser.parse_args()
args.annnotation_file1 = os.path.normpath(args.annotation_file1)
args.annnotation_file2 = os.path.normpath(args.annotation_file2)
args.output_annotation = os.path.normpath(args.output_annotation)

with open(args.annotation_file1) as file1:
    with open(args.annotation_file2) as file2:
        file1_json = json.load(file1)
        file2_json = json.load(file2)
        with open(args.output_annotation, "w") as output_file:
            json.dump(file1_json | file2_json, output_file)
