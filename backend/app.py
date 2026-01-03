from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np

app = Flask(__name__)
CORS(app)

# ---------------- LOAD MODEL ----------------

with open("../ml/ml/stress_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("../ml/ml/label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)


# ---------------- NORMALIZATION FUNCTIONS ----------------

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


# ---------------- ML PREDICTION API ----------------

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    features = np.array([[  
        data["sleep"],
        data["study"],
        data["screen"],
        data["activity"],
        data["mood"]
    ]])

    prediction = model.predict(features)
    stress_label = label_encoder.inverse_transform(prediction)[0]

    return jsonify({
        "predicted_stress": stress_label
    })


# ---------------- IKIGAI + EXPLAINABLE SCORING API ----------------

@app.route("/ikigai", methods=["POST"])
def ikigai():
    data = request.get_json()

    # ---------- Layer 1: Normalization ----------
    sleep_score = normalize_sleep(data["sleep"])
    study_score = normalize_study(data["study"])
    screen_score = normalize_screen(data["screen"])
    activity_score = normalize_activity(data["activity"])
    mood_score = normalize_mood(data["mood"])

    # ---------- Layer 2: Stress & Productivity ----------
    stress_score = (
        0.30 * sleep_score +
        0.25 * mood_score +
        0.20 * screen_score +
        0.15 * study_score +
        0.10 * activity_score
    )

    if stress_score >= 75:
        rule_based_stress = "Low"
    elif stress_score >= 50:
        rule_based_stress = "Medium"
    else:
        rule_based_stress = "High"

    productivity_score = (
        0.40 * study_score +
        0.30 * sleep_score +
        0.20 * activity_score +
        0.10 * screen_score
    )

    # ---------- Layer 3: Ikigai ----------
    love = (mood_score + activity_score) / 2
    good_at = study_score
    need = (sleep_score + (100 - stress_score)) / 2
    value = productivity_score

    ikigai_score = (love + good_at + need + value) / 4

    # ---------- ML Support (Not Final Authority) ----------
    features = np.array([[  
        data["sleep"],
        data["study"],
        data["screen"],
        data["activity"],
        data["mood"]
    ]])

    ml_prediction = model.predict(features)
    ml_stress = label_encoder.inverse_transform(ml_prediction)[0]

    # ---------- Safety Overrides (Ethical Layer) ----------
    final_stress = rule_based_stress

    if data["sleep"] < 4 or data["mood"] <= 2:
        final_stress = "Medium"

    if data["sleep"] < 3 and data["screen"] > 6:
        final_stress = "High"

    # ---------- Final Response ----------
    return jsonify({
        "layer1_normalized": {
            "sleep_score": round(sleep_score, 2),
            "study_score": round(study_score, 2),
            "screen_score": round(screen_score, 2),
            "activity_score": round(activity_score, 2),
            "mood_score": round(mood_score, 2)
        },
        "layer2_scores": {
            "stress_score": round(stress_score, 2),
            "rule_based_stress": rule_based_stress,
            "productivity_score": round(productivity_score, 2)
        },
        "layer3_ml_support": {
            "ml_predicted_stress": ml_stress,
            "final_stress_level": final_stress
        },
        "layer3_ikigai": {
            "love": round(love, 2),
            "good_at": round(good_at, 2),
            "need": round(need, 2),
            "value": round(value, 2),
            "ikigai_score": round(ikigai_score, 2)
        }
    })


# ---------------- HOME ----------------

@app.route("/")
def home():
    return "Server is running"


if __name__ == "__main__":
    app.run(debug=True)

