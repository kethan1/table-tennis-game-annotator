import os
import argparse
import cv2
from model_abstractions import YOLOv5_Model
from calculate_parabola_equation import calculate_parabola_equation


parser = argparse.ArgumentParser()
parser.add_argument(
    "--model", default="data/weights/ball_detection_model.pt", help="path to model"
)
parser.add_argument("--video", default="data/test_4.mp4", help="path to video")
parser.add_argument(
    "--starting-frame", type=int, default=0, help="the frame to start video analysis at"
)
parser.add_argument(
    "--skip-frames", type=int, default=1, help="every nth frame to analyze"
)

args = parser.parse_args()
args.model = os.path.normpath(args.model)
args.video = os.path.normpath(args.video)


cap = cv2.VideoCapture(args.video)
ball_detection_model = YOLOv5_Model(args.model)

i = 0
cap.set(cv2.CAP_PROP_POS_FRAMES, args.starting_frame)
same_dir_ball_detections = []
while True:
    i += 1
    ret, frame = cap.read()
    if not ret:
        break
    if i % parser.skip_frames != 0:
        continue
    if predictions := ball_detection_model.predict_coords(
        ball_detection_model.process_opencv_image(frame)
    ):
        ball = max(predictions, key=lambda x: x.confidence)
        xmin, ymin, xmax, ymax, confidence, name = ball.values()
        xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
        same_dir_ball_detections.append(ball)
        prev_prev_ball = same_dir_ball_detections[-3]
        prev_ball = same_dir_ball_detections[-2]
        if len(same_dir_ball_detections) > 2:
            prev_x_moved = prev_prev_ball["xmin"] - prev_ball["xmin"]
            prev_y_moved = prev_prev_ball["ymin"] - prev_ball["ymin"]
            current_x_moved = prev_ball["xmin"] - xmin
            current_y_moved = prev_ball["ymin"] - ymin
            if prev_x_moved * current_x_moved < 0 or prev_y_moved * current_y_moved < 0:
                same_dir_ball_detections = same_dir_ball_detections[-2:]
            else:
                equation = calculate_parabola_equation(
                    prev_prev_ball["xmin"] + 7,
                    prev_prev_ball["ymin"] + 7,
                    prev_ball["xmin"] + 7,
                    prev_ball["ymin"] + 7,
                    xmin + 7,
                    ymin + 7,
                )
                for x in range(0, frame.shape[1], 5):
                    cv2.circle(
                        frame,
                        (x, equation(x)),
                        radius=2,
                        color=(0, 255, 0),
                        thickness=-1,
                    )
        for detection in same_dir_ball_detections:
            cv2.circle(
                frame,
                (
                    (detection["xmin"] + detection["xmax"]) // 2,
                    (detection["ymin"] + detection["ymax"]) // 2,
                ),
                radius=9,
                color=(0, 0, 255),
                thickness=-1,
            )
    frame = cv2.resize(frame, (1080, 607))
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
