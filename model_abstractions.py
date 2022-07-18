import abc
from collections import Counter
import torch
from PIL import Image


class Model(abc.ABC):
    def __init__(self, model_path=None, *args, **kwargs):
        if model_path is not None:
            self.load_model(model_path, *args, **kwargs)

    @abc.abstractmethod
    def load_model(self, model_path):
        raise NotImplementedError

    @abc.abstractmethod
    def predict(self, image_path):
        raise NotImplementedError


class YOLOv5_Model(Model):
    def load_model(self, model_path=None, *args, **kwargs):
        self.model = torch.hub.load(
            "ultralytics/yolov5", "custom", path=model_path, *args, **kwargs
        )

    def load_image(self, image_path):
        return Image.open(image_path)

    def process_opencv_image(self, image):
        return image[..., ::-1]

    def predict(self, image, min_confidence=0):
        results = self.model(image)
        df = results.pandas().xyxy[0][["confidence", "name"]]
        df["confidence"] = df[df["confidence"] > min_confidence]["confidence"]
        df.dropna(inplace=True)
        return dict(Counter(df.name.tolist()))

    def predict_coords(self, image, min_confidence=0.4):
        results = self.model(image)
        df = results.pandas().xyxy[0]
        df["confidence"] = df[df["confidence"] > min_confidence]["confidence"]
        df.dropna(inplace=True)
        df.drop("class", axis=1, inplace=True)
        return df.to_dict("records")


class COCO128_Model(YOLOv5_Model):
    def __init__(self):
        self.load_model()

    def load_model(self, model_type="yolov5s6"):
        if model_type not in [
            "yolov5n",
            "yolov5s",
            "yolov5m",
            "yolov5x",
            "yolov5n6",
            "yolov5s6",
            "yolov5m6",
            "yolov5x6",
        ]:
            raise ValueError(
                "model_type must be one of ['yolov5n', 'yolov5s', 'yolov5m', 'yolov5x', 'yolov5n6', 'yolov5s6', 'yolov5m6', 'yolov5x6']"
            )
        self.model = torch.hub.load("ultralytics/yolov5", "yolov5s6")
