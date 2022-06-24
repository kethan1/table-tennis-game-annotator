import cv2
import os
import json


basepath = "data/test2/"
cap = cv2.VideoCapture(os.path.join(basepath, "game.mp4"))
annotated_frames = os.listdir(os.path.join(basepath, "segmentation_masks"))
with open(os.path.join(basepath, "ball_markup.json")) as ball_markup_file:
    ball_pos_data = json.load(ball_markup_file)

num = basepath.strip("/")[-1]
add_str = "" if num == "1" else f"_{num}"
while True:
    ret, frame = cap.read()
    if not ret:
        break
    segmentation_mask_name = f"{int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1}.png"
    if segmentation_mask_name in annotated_frames:
        cv2.imwrite(os.path.join(basepath, "segmentation_images", f"{str(int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1)}{add_str}.png"), frame)

cap.release()
cv2.destroyAllWindows()
