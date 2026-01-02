from flask import Flask, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# Load trained model and encoder
with open("../ml/ml/stress_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("../ml/ml/label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

def normalize_sleep(sleep):
    if 7 <= sleep <= 8:
        return 100
    elif 6 <= sleep < 7 or 8 < sleep <= 9:
        return 80
    elif 5 <= sleep < 6 or 9 < sleep <= 10:
        return 60
    else:
        return 30


def normalize_study(study):
    if 4 <= study <= 6:
        return 90
    elif 2 <= study < 4 or 6 < study <= 8:
        return 75
    else:
        return 50


def normalize_screen(screen):
    if screen <= 2:
        return 90
    elif screen <= 4:
        return 75
    elif screen <= 6:
        return 50
    else:
        return 30


def normalize_activity(activity):
    if activity >= 30:
        return 90
    elif activity >= 15:
        return 70
    else:
        return 40


def normalize_mood(mood):
    return (mood / 5) * 100

@app.route("/predict", methods=["POST"])
@app.route("/ikigai", methods=["POST"])
def ikigai():
    data = request.get_json()

    # Normalize inputs
    sleep_score = normalize_sleep(data["sleep"])
    study_score = normalize_study(data["study"])
    screen_score = normalize_screen(data["screen"])
    activity_score = normalize_activity(data["activity"])
    mood_score = normalize_mood(data["mood"])

    # Stress score (rule-based, explainable)
    stress_score = (
        0.30 * sleep_score +
        0.25 * mood_score +
        0.20 * screen_score +
        0.15 * study_score +
        0.10 * activity_score
    )

    # Ikigai pillars
    love = (mood_score + activity_score) / 2
    good_at = study_score
    need = (sleep_score + (100 - stress_score)) / 2
    value = (
        0.40 * study_score +
        0.30 * sleep_score +
        0.20 * activity_score +
        0.10 * screen_score
    )

    ikigai_score = (love + good_at + need + value) / 4

    return jsonify({
        "ikigai_score": round(ikigai_score, 2),
        "pillars": {
            "love": round(love, 2),
            "good_at": round(good_at, 2),
            "need": round(need, 2),
            "value": round(value, 2)
        }
    })

def predict():
    data = request.get_json()

    # Extract input values
    features = np.array([[
        data["sleep"],
        data["study"],
        data["screen"],
        data["activity"],
        data["mood"]
    ]])

    # Predict
    prediction = model.predict(features)
    stress_label = label_encoder.inverse_transform(prediction)[0]

    return jsonify({
        "predicted_stress": stress_label
    })

@app.route("/")
def home():
    return "Server is running"

if __name__ == "__main__":
    app.run(debug=True)
