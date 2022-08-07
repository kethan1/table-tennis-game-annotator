import os
import json
import argparse
import cv2
import imagesize
from tqdm import tqdm


parser = argparse.ArgumentParser()
parser.add_argument(
    "--data-path",
    help="path to a folder containing the images",
    default="data/test1",
)
parser.add_argument(
    "--images-path",
    help="path to a folder containing the images",
    default="segmentation_images",
)
parser.add_argument(
    "--masks-path",
    help="path to the annotations",
    default="segmentation_masks",
)

args = parser.parse_args()
args.images_path = os.path.normpath(args.images_path)
args.masks_path = os.path.normpath(args.masks_path)


def generate_vgg_annotation(image_path, segmentation_mask_path):
    segmentation_mask = cv2.imread(segmentation_mask_path)
    segmentation_mask = cv2.resize(segmentation_mask, imagesize.get(image_path))

    # Read the binary mask, and find the contours associated
    table, players, scoreboard = seperate_channels(segmentation_mask)

    table = cv2.cvtColor(table, cv2.COLOR_BGR2GRAY)
    players = cv2.cvtColor(players, cv2.COLOR_BGR2GRAY)
    scoreboard = cv2.cvtColor(scoreboard, cv2.COLOR_BGR2GRAY)

    _, table = cv2.threshold(table, 1, 255, 0)
    _, players = cv2.threshold(players, 1, 255, 0)
    _, scoreboard = cv2.threshold(scoreboard, 1, 255, 0)

    table_contours, _ = cv2.findContours(table, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    players_contours, _ = cv2.findContours(
        players, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE
    )
    scoreboard_contours, _ = cv2.findContours(
        scoreboard, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE
    )

    # -------------------------------------------------------------------------------
    # BUILDING VGG ANNTOTATION TOOL ANNOTATIONS LIKE
    if table_contours or players_contours or scoreboard_contours:
        table_regions = [0] * len(table_contours)
        for i in range(len(table_contours)):
            table_regions[i] = {
                "shape_attributes": {
                    "name": "polygon",
                    "all_points_x": table_contours[i][:, 0][:, 0].tolist(),
                    "all_points_y": table_contours[i][:, 0][:, 1].tolist(),
                },
                "region_attributes": {"class": "table"},
            }

        players_regions = [0] * len(players_contours)
        for i in range(len(players_contours)):
            players_regions[i] = {
                "shape_attributes": {
                    "name": "polygon",
                    "all_points_x": players_contours[i][:, 0][:, 0].tolist(),
                    "all_points_y": players_contours[i][:, 0][:, 1].tolist(),
                },
                "region_attributes": {"class": "players"}
            }

        scoreboard_regions = [0] * len(scoreboard_contours)
        for i in range(len(scoreboard_contours)):
            scoreboard_regions[i] = {
                "shape_attributes": {
                    "name": "polygon",
                    "all_points_x": scoreboard_contours[i][:, 0][:, 0].tolist(),
                    "all_points_y": scoreboard_contours[i][:, 0][:, 1].tolist(),
                },
                "region_attributes": {"class": "scoreboard"},
            }

        regions = dict(enumerate(table_regions + players_regions + scoreboard_regions))

        size = os.path.getsize(image_path)
        name = os.path.basename(image_path) + str(size)
        json_elt = {"filename": os.path.basename(image_path)}
        json_elt["size"] = str(size)
        json_elt["regions"] = regions
        json_elt["file_attributes"] = {}
        return {name: json_elt}


def seperate_channels(image):
    b = image.copy()
    # set green and red channels to 0
    b[:, :, 1] = 0
    b[:, :, 2] = 0

    g = image.copy()
    # set blue and red channels to 0
    g[:, :, 0] = 0
    g[:, :, 2] = 0

    r = image.copy()
    # set blue and green channels to 0
    r[:, :, 0] = 0
    r[:, :, 1] = 0

    return r, g, b


num = os.path.basename(args.data_path)[-1]
suffix = "" if num == "1" else f"_{num}"
final_dict = {}
for image in tqdm(os.listdir(os.path.join(args.data_path, args.masks_path))):
    final_dict |= generate_vgg_annotation(
        os.path.join(
            args.data_path, args.images_path, image.strip(".png") + f"{suffix}.png"
        ),
        os.path.join(args.data_path, args.masks_path, image),
    )


with open(os.path.join(args.data_path, "via_region_data.json"), "w") as json_file:
    json.dump(final_dict, json_file)
