import os
import json
import argparse
from pprint import pprint
import cv2
import numpy as np


parser = argparse.ArgumentParser()
parser.add_argument(
    "--annotation-file-path",
    help="path to the annotation file",
)
parser.add_argument(
    "--annotation-file-key",
    help="relevant annotation file key",
)

args = parser.parse_args()
args.annotation_file_path = os.path.normpath(args.annotation_file_path)


def create_blank(width, height, rgb_color=(0, 0, 0)):
    """Create new image(numpy array) filled with certain color in RGB"""
    # Create black blank image
    image = np.zeros((height, width, 3), np.uint8)

    # Since OpenCV uses BGR, convert the color first
    color = tuple(reversed(rgb_color))
    # Fill image with color
    image[:] = color

    return image


with open(args.annotation_file_path, "r") as annotation_file:
    annotation_json = json.load(annotation_file)

blank_image = create_blank(1920, 1080)
for region in annotation_json[args.annotation_file_key]["regions"].values():
    coords = list(zip(region["shape_attributes"]["all_points_x"], region["shape_attributes"]["all_points_y"]))

    shape = np.array([[list(coord) for coord in coords]], np.int32)
    cv2.polylines(blank_image, [shape], True, (0, 255, 0), thickness=3)

# blank_image = cv2.resize(blank_image, (960, 540))

# print(blank_image.shape)

cv2.imshow("image", blank_image)
cv2.waitKey(0)
