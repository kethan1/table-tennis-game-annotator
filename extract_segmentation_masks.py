import os
import argparse
import cv2


parser = argparse.ArgumentParser()
parser.add_argument(
    "--data-path",
    help="path to a folder containing the images",
    default="data/test1/",
)
parser.add_argument(
    "--game-file",
    help="path to the annotations",
    default="game.mp4",
)
parser.add_argument(
    "--segmentation-images-folder",
    help="path to the annotations",
    default="segmentation_masks",
)
parser.add_argument(
    "--output-folder",
    help="path to the annotations",
    default="segmentation_images",
)

args = parser.parse_args()
args.data_path = os.path.normpath(args.data_path)
args.game_file = os.path.normpath(args.game_file)
args.segmentation_images_folder = os.path.normpath(args.segmentation_images_folder)
args.output_folder = os.path.normpath(args.output_folder)

cap = cv2.VideoCapture(os.path.join(args.data_path, args.game_file))
annotated_frames = os.listdir(
    os.path.join(args.data_path, args.segmentation_images_folder)
)

num = os.path.basename(args.data_path)[-1]
suffix = "" if num == "1" else f"_{num}"

while True:
    ret, frame = cap.read()
    if not ret:
        break
    segmentation_mask_name = f"{int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1}.png"
    if segmentation_mask_name in annotated_frames:
        cv2.imwrite(
            os.path.join(
                args.data_path,
                args.output_folder,
                f"{str(int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1)}{suffix}.png",
            ),
            frame,
        )

cap.release()
cv2.destroyAllWindows()
