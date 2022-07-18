from flask import Flask, render_template, request
from PIL import Image
from model_abstractions import YOLOv5_Model
from parabola_manipulation import calculate_parabola_parameters

app = Flask(__name__, template_folder="dist/templates", static_folder="dist/static")
ball_detection_model = YOLOv5_Model("weights/ball_detection_model.pt")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/analyze_gameplay")
def analyze_gameplay():
    return render_template("analyze_gameplay.html")


@app.route("/api/v1/detect-ball", methods=["POST"])
def detect_ball():
    image = Image.open(request.files["file"])
    if predictions := ball_detection_model.predict_coords(image):
        return max(predictions, key=lambda x: x["confidence"])
    return {}


@app.route("/api/v1/calculate_parabola", methods=["POST"])
def calculate_parabola():
    # structure: {'point1': {'x': 1, 'y': 2}, 'point2': {'x': 3, 'y': 4}, 'point3': {'x': 5, 'y': 6}}
    (x1, y1), (x2, y2), (x3, y3) = map(dict.values, request.json.values())
    A, B, C = calculate_parabola_parameters(x1, y1, x2, y2, x3, y3)
    return {"A": A, "B": B, "C": C}


if __name__ == "__main__":
    app.run(debug=True)
