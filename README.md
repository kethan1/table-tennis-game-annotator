# Table Tennis Game Annotater
This repo aims to provide useful live annotatation during a table tennis game.

This repo aims to create two models. One to detect the position of the ball and the other to detect various objects in the scene using instance segmentation. The instance segmentation model should detect the players, the table, and the scoreboard. 

# Data
The data used was from https://lab.osai.ai/. Specifically, games 1 through 3 in the train data and and games 1 through 3 in the test data. This data was processed into the YOLOv5 format for the ball detection model and the vgg annotation format for the instance segmentation model. 

# Machine Learning Models

## Ball Detection Model
For the ball detection model, I chose to use [YOLOv5](https://github.com/ultralytics/yolov5) for its high accuracy and speed. The YOLOv5 model is trained on a processed version of the above mentioned data source. I have uploaded the processed data to Kaggle: https://www.kaggle.com/datasets/ketzoomer/table-tennis-ball-detection-dataset. 

## Instance Segmentation Model
For the instance segmentation model, I used the [Mask R-CNN model implementation by matterport](https://github.com/matterport/Mask_RCNN). The data for this model has not been fully processed yet.
