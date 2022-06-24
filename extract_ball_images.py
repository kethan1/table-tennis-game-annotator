import cv2
import os
import json


basepath = "data/test3/"
cap = cv2.VideoCapture(os.path.join(basepath, "game.mp4"))
with open(os.path.join(basepath, "ball_markup.json")) as ball_markup_file:
    ball_pos_data = json.load(ball_markup_file)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if str(int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1) in ball_pos_data:
        cv2.imwrite(os.path.join(basepath, "ball_images", f"{str(int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1)}_3.png"), frame)

cap.release()
cv2.destroyAllWindows()
