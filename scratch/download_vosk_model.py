# download_vosk_model.py - Script to download and extract a small Vosk model for wake-word detection.

import os
import urllib.request
import zipfile
from pathlib import Path

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
MODEL_NAME = "vosk-model-small-en-us-0.15"
MODELS_DIR = Path("zerobot/assets/models")

def download_and_extract():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = MODELS_DIR / f"{MODEL_NAME}.zip"
    model_path = MODELS_DIR / MODEL_NAME

    if model_path.exists():
        print(f"Model already exists at {model_path}")
        return

    print(f"Downloading Vosk model from {MODEL_URL}...")
    urllib.request.urlretrieve(MODEL_URL, zip_path)
    
    print(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(MODELS_DIR)
    
    os.remove(zip_path)
    print("Done! Vosk model is ready.")

if __name__ == "__main__":
    download_and_extract()
