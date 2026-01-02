from flask import Flask, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# Load trained model and encoder
with open("../ml/ml/stress_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("../ml/ml/label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

@app.route("/predict", methods=["POST"])
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
