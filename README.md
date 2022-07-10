# Table Tennis Game Annotater
This repo aims to provide useful live annotatation during a table tennis game.

To fulfil with aim, this repo intends to create two models. One to detect the position of the ball using object detection and the other to detect various objects in the scene using instance segmentation. The instance segmentation model should detect the players, the table, and the scoreboard. 

## Data
The data used was from https://lab.osai.ai/. Specifically, the training data consisted of games 1 through 3 and the testing data consisted of games 1 through 3. The data and annotations were processed into the YOLOv5 format for the ball detection model and the vgg annotation format for the instance segmentation model. 

Ball Detection Model Processed Data - https://www.kaggle.com/datasets/ketzoomer/table-tennis-ball-position-detection-dataset
Instance Segmentation Model Processed Data - Coming Soon

## Machine Learning Models

### Ball Detection Model
For the ball detection model, I chose to use [YOLOv5](https://github.com/ultralytics/yolov5) for its high accuracy and speed. The [YOLOv5](https://github.com/ultralytics/yolov5) model uses the (YOLOv5m6)[https://github.com/ultralytics/yolov5#:~:text=16.8-,YOLOv5m6,-1280] configuration and it was trained on the above mentioned processed data.

### Instance Segmentation Model
For the instance segmentation model, I used the [Mask R-CNN implementation by matterport](https://github.com/matterport/Mask_RCNN). The data for this model has not been fully processed yet.
