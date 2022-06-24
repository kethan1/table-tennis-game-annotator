import cv2
import os
import json


basepath = "data/game2/"
cap = cv2.VideoCapture(os.path.join(basepath, "game.mp4"))
annotated_frames = os.listdir(os.path.join(basepath, "segmentation_masks"))
with open(os.path.join(basepath, "ball_markup.json")) as ball_markup_file:
    ball_pos_data = json.load(ball_markup_file)

while True:
    ret, original_frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(original_frame, (1080, 608))
    segmentation_mask_name = f"{int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1}.png"
    if segmentation_mask_name in annotated_frames:
        segmentation_mask = cv2.imread(
            os.path.join(basepath, "segmentation_masks", segmentation_mask_name)
        )
        segmentation_mask = cv2.resize(segmentation_mask, (1080, 608))
        frame = cv2.addWeighted(frame, 1, segmentation_mask, 1, 0)

    if str(int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1) in ball_pos_data:
        ball_pos = ball_pos_data[str(int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1)]
        ball_pos_x, ball_pos_y = int(ball_pos["x"] * (608 / 1080)), int(
            ball_pos["y"] * (1080 / 1920)
        )
        cv2.rectangle(
            frame,
            (ball_pos_x - 6, ball_pos_y + 6),
            (ball_pos_x + 6, ball_pos_y - 6),
            (255, 0, 0),
            1,
        )
        
        cv2.imshow("Frame", frame)
        cv2.waitKey(0)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
