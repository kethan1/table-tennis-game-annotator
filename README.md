# Table Tennis Game Annotater
This repo aims to provide useful live annotatation during a table tennis game through a website.

To fulfil with aim, this repo intends to create two models. One to detect the position of the ball using object detection and the other to detect various objects in the scene using instance segmentation. The instance segmentation model should detect the players, the table, and the scoreboard. 

To accomplish the goal of having this functionality available through a website, this repo contains the code for a Flask server and uses ncnn through webassembly for the client-side ball detection model inference.

## Data
The data used was from https://lab.osai.ai/. Specifically, the training data consisted of games 1 through 3 and the testing data consisted of games 1 through 3. The data and annotations were processed into the YOLOv5 format for the ball detection model and the vgg annotation format for the instance segmentation model. 

Ball Detection Model Processed Data - https://www.kaggle.com/datasets/ketzoomer/table-tennis-ball-position-detection-dataset
Instance Segmentation Model Processed Data - https://www.kaggle.com/datasets/ketzoomer/table-tennis-segmentation-masks-for-scene-analysis

## Machine Learning Models

### Ball Detection Model
For the ball detection model, I chose to use [YOLOv5](https://github.com/ultralytics/yolov5) for its high accuracy and speed. The [YOLOv5](https://github.com/ultralytics/yolov5) model uses the [YOLOv5m6](https://github.com/ultralytics/yolov5#:~:text=16.8-,YOLOv5m6,-1280) configuration and it was trained on the above mentioned processed data.

### Instance Segmentation Model
For the instance segmentation model, I forked the [Mask R-CNN implementation by matterport](https://github.com/matterport/Mask_RCNN) to [Mask R-CNN TF2](https://github.com/kethan1/Mask_RCNN_TF2) and added support for Tensorflow 2 and the latest version of scikit-image.
