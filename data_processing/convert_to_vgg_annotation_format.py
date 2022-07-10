import os
import json
import argparse
import cv2
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


def generate_vgg_annotation(
    image_path, segmentation_mask_path, res=0.6, surf=100, eps=0.01
):
    """
    res : spatial resolution of images in meter
    surf : the minimum surface of roof considered in the study in square meter
    eps : the index for Ramer–Douglas–Peucker (RDP) algorithm for contours approx to decrease nb of points describing a contours
    """

    # Read the binary mask, and find the contours associated
    table, players, scoreboard = seperate_channels(cv2.imread(segmentation_mask_path))

    table = cv2.cvtColor(table, cv2.COLOR_BGR2GRAY)
    players = cv2.cvtColor(players, cv2.COLOR_BGR2GRAY)
    scoreboard = cv2.cvtColor(scoreboard, cv2.COLOR_BGR2GRAY)

    _, table = cv2.threshold(table, 1, 255, 0)
    _, players = cv2.threshold(players, 1, 255, 0)
    _, scoreboard = cv2.threshold(scoreboard, 1, 255, 0)

    table_contours, _ = cv2.findContours(table, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    players_contours, _ = cv2.findContours(
        players, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    scoreboard_contours, _ = cv2.findContours(
        scoreboard, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    # https://www.pyimagesearch.com/2021/10/06/opencv-contour-approximation/
    # Contours approximation based on Ramer–Douglas–Peucker (RDP) algorithm
    table_areas = [
        cv2.contourArea(table_contours[idx]) * res * res
        for idx in range(len(table_contours))
    ]
    table_large_contour = [
        table_contours[i] for i in range(len(table_areas)) if table_areas[i] > surf
    ]
    table_approx_contour = [
        cv2.approxPolyDP(c, eps * cv2.arcLength(c, True), True)
        for c in table_large_contour
    ]

    players_areas = [
        cv2.contourArea(players_contours[idx]) * res * res
        for idx in range(len(players_contours))
    ]
    players_large_contour = [
        players_contours[i]
        for i in range(len(players_areas))
        if players_areas[i] > surf
    ]
    players_approx_contour = [
        cv2.approxPolyDP(c, eps * cv2.arcLength(c, True), True)
        for c in players_large_contour
    ]

    scoreboard_areas = [
        cv2.contourArea(scoreboard_contours[idx]) * res * res
        for idx in range(len(scoreboard_contours))
    ]
    scoreboard_large_contour = [
        scoreboard_contours[i]
        for i in range(len(scoreboard_areas))
        if scoreboard_areas[i] > surf
    ]
    scoreboard_approx_contour = [
        cv2.approxPolyDP(c, eps * cv2.arcLength(c, True), True)
        for c in scoreboard_large_contour
    ]

    # -------------------------------------------------------------------------------
    # BUILDING VGG ANNTOTATION TOOL ANNOTATIONS LIKE
    if table_approx_contour or players_approx_contour or scoreboard_approx_contour:
        table_regions = [0] * len(table_approx_contour)
        for i in range(len(table_approx_contour)):
            region_attributes = {"class": "table"}
            shape_attributes = {
                "name": "polygon",
                "all_points_x": table_approx_contour[i][:, 0][:, 0].tolist(),
            }

            # https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable
            shape_attributes["all_points_y"] = table_approx_contour[i][:, 0][
                :, 1
            ].tolist()
            regionsi = {
                "shape_attributes": shape_attributes,
                "region_attributes": region_attributes,
            }

            table_regions[i] = regionsi

        players_regions = [0] * len(players_approx_contour)
        for i in range(len(players_approx_contour)):
            shape_attributes = {}
            region_attributes = {"class": "players"}
            regionsi = {}
            shape_attributes["name"] = "polygon"
            shape_attributes["all_points_x"] = players_approx_contour[i][:, 0][
                :, 0
            ].tolist()
            # https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable
            shape_attributes["all_points_y"] = players_approx_contour[i][:, 0][
                :, 1
            ].tolist()
            regionsi["shape_attributes"] = shape_attributes
            regionsi["region_attributes"] = region_attributes
            players_regions[i] = regionsi

        scoreboard_regions = [0] * len(scoreboard_approx_contour)
        for i in range(len(scoreboard_approx_contour)):
            shape_attributes = {}
            region_attributes = {"class": "scoreboard"}
            regionsi = {}
            shape_attributes["name"] = "polygon"
            shape_attributes["all_points_x"] = scoreboard_approx_contour[i][:, 0][
                :, 0
            ].tolist()
            # https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable
            shape_attributes["all_points_y"] = scoreboard_approx_contour[i][:, 0][
                :, 1
            ].tolist()
            regionsi["shape_attributes"] = shape_attributes
            regionsi["region_attributes"] = region_attributes
            scoreboard_regions[i] = regionsi

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


with open(
    os.path.join(
        os.path.dirname(os.path.join(args.data_path, args.images_path)),
        "via_region_data.json",
    ),
    "w",
) as json_file:
    json.dump(final_dict, json_file)
