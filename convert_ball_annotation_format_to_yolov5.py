import os
import cv2
import argparse
import json
from typing import List
from tqdm import tqdm


parser = argparse.ArgumentParser()
parser.add_argument(
    "--data-path",
    help="path to a folder containing the images",
    default="data/game1/",
)
parser.add_argument(
    "--images-path",
    help="path to a folder containing the images",
    default="ball_images",
)
parser.add_argument(
    "--annotations",
    help="path to the annotations",
    default="ball_markup.json",
)
parser.add_argument(
    "--output-folder",
    help="output of the annotations",
    default="ball_images",
)

args = parser.parse_args()
args.data_path = os.path.normpath(args.data_path)
args.images_path = os.path.normpath(args.images_path)
args.annotations = os.path.normpath(args.annotations)
args.output_folder = os.path.normpath(args.output_folder)


classes = ["ball"]


def create_annotation(imgfilepath: str, classname: str, coords: List[str]):
    """
    params:
    - imgfilepath: path of corresponding img file. only the basename will be actually used.
    - classname: the class that the image belongs to
    - object_list: python list of objects. Formatted like so [min_x, min_y, max_x, max_y]
    - savedir: output directory to save generated txt file
    """

    image = cv2.imread(imgfilepath)
    height, width = image.shape[0], image.shape[1]

    roi_width = coords[2] - coords[0]
    roi_height = coords[3] - coords[1]

    roi_center_x = (coords[0] + coords[2]) / 2
    roi_center_y = (coords[1] + coords[3]) / 2
    with open(
        os.path.join(
            args.data_path,
            args.output_folder,
            "".join(os.path.basename(imgfilepath).split(".")[:-1]) + ".txt",
        ),
        "w",
    ) as output_file:
        print(
            f"{classes.index(classname)} {roi_center_x / width} {roi_center_y / height} {roi_width / width} {roi_height / height}",
            file=output_file,
        )


num = os.path.basename(args.data_path)[-1]
suffix = "" if num == "1" else f"_{num}"
with open(os.path.join(args.data_path, args.annotations)) as annotations:
    annotations_json = json.load(annotations)
    for key, value in tqdm(annotations_json.items()):
        file = os.path.join(args.data_path, args.images_path, f"{int(key)}{suffix}.png")
        x, y = value["x"], value["y"]
        if x == -1 or y == -1:
            continue
        x1, y1 = x - 6, y + 6
        x2, y2 = x + 6, y - 6
        if os.path.exists(file):
            create_annotation(file, "ball", [x1, y2, x2, y1])
