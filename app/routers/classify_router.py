# app/routers/image_router.py

import os
import uuid
import numpy as np
from flask import Blueprint, request, jsonify, current_app
from PIL import Image

from app.services.get_classification import classify
from app.services.get_preprocess import preprocess

classify_bp = Blueprint("classify", __name__)
classes = ["0 - No_DR",
"1 - Mild",
"2 - Moderate",
"3 - Severe",
"4 - Proliferate_DR"]

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@classify_bp.route("/api/classify", methods=["POST"])
def api_classify():
    if "image" not in request.files:
        return jsonify({"error": "No file part named 'image'"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"Invalid extension. Allowed: {ALLOWED_EXTENSIONS}"}), 400

    # Save the raw upload to static/uploads/
    raw_ext = os.path.splitext(file.filename)[1].lower()  # includes dot, e.g. ".jpg"
    raw_filename = f"{uuid.uuid4().hex}{raw_ext}"
    upload_folder = os.path.join(current_app.root_path, "static", "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    raw_path = os.path.join(upload_folder, raw_filename)
    file.save(raw_path)

    try:
        pil_img = Image.open(raw_path).convert("RGB")
        img_array = np.asarray(pil_img)  # shape: (H,W,3), dtype=uint8

        # Preprocess + classify
        processed_array = preprocess(img_array)  # (224,224,3) uint8
        pred_class = classify(img_array)    # returns an int
        print(f"PREDCLASS : {classes[pred_class]}") #get class name

        # Save the preprocessed array to static/processed/
        proc_filename = f"{uuid.uuid4().hex}.png"
        processed_folder = os.path.join(current_app.root_path, "static", "processed")
        os.makedirs(processed_folder, exist_ok=True)
        proc_path = os.path.join(processed_folder, proc_filename)

        # Convert the NumPy array back to PIL and save as PNG
        Image.fromarray(processed_array).save(proc_path, format="PNG")

        # Build the public URLs
        raw_url = f"/static/uploads/{raw_filename}"
        proc_url = f"/static/processed/{proc_filename}"

    except Exception as e:
        current_app.logger.exception("Error during preprocessing/classification")
        return jsonify({"error": "Server failed during processing"}), 500

    # Return JSON with both URLs and the predicted class
    return jsonify({
        "raw_url": raw_url,
        "processed_url": proc_url,
        "classification": classes[pred_class]
    }), 200
