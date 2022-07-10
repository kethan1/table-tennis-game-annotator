import os
import json
import argparse
import cv2


parser = argparse.ArgumentParser()
parser.add_argument(
    "--data-path",
    help="path to a folder containing the images",
    default="data/game1/",
)
parser.add_argument(
    "--game-file",
    help="path to the video",
    default="game.mp4",
)
parser.add_argument(
    "--annotation-file",
    help="path to the annotations",
    default="ball_markup.json",
)
parser.add_argument(
    "--output-folder",
    help="path to the annotations",
    default="ball_images",
)

args = parser.parse_args()
args.data_path = os.path.normpath(args.data_path)
args.game_file = os.path.normpath(args.game_file)
args.annotation_file = os.path.normpath(args.annotation_file)
args.output_folder = os.path.normpath(args.output_folder)

if not os.path.isdir(os.path.join(args.data_path, args.output_folder)):
    os.mkdir(os.path.join(args.data_path, args.output_folder))


cap = cv2.VideoCapture(os.path.join(args.data_path, args.game_file))
with open(os.path.join(args.data_path, args.annotation_file)) as ball_markup_file:
    ball_pos_data = json.load(ball_markup_file)


num = os.path.basename(args.data_path)[-1]
suffix = "" if num == "1" else f"_{num}"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_name = str(int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1)
    if frame_name in ball_pos_data:
        cv2.imwrite(
            os.path.join(
                args.data_path, args.output_folder, f"{frame_name}{suffix}.png"
            ),
            frame,
        )

cap.release()
cv2.destroyAllWindows()
