"""
SmartRoad AI — Model Weights Download & Verification Script
Downloads pre-trained YOLO pothole detection model weights from Hugging Face
and verifies compatibility with Ultralytics and PyTorch.
"""

import os
import sys
import time
import urllib.request

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
WEIGHTS_PATH = os.path.join(MODELS_DIR, "pothole_best.pt")

# Direct weights URL from Hugging Face
URL = "https://huggingface.co/peterhdd/pothole-detection-yolov8/resolve/main/best.pt"

def download_progress(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size) if total_size > 0 else 0
    downloaded_mb = count * block_size / (1024 * 1024)
    total_mb = total_size / (1024 * 1024)
    sys.stdout.write(f"\rDownloading YOLO weights: {percent}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)")
    sys.stdout.flush()

def main():
    os.makedirs(MODELS_DIR, exist_ok=True)
    print(f"Target path: {WEIGHTS_PATH}")
    print(f"Fetching from: {URL}")

    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(URL, headers=headers)
    
    start = time.time()
    with urllib.request.urlopen(req) as response, open(WEIGHTS_PATH, 'wb') as out_file:
        total_size = int(response.info().get('Content-Length', -1))
        block_size = 1024 * 64
        count = 0
        while True:
            chunk = response.read(block_size)
            if not chunk:
                break
            out_file.write(chunk)
            count += 1
            if total_size > 0:
                download_progress(count, block_size, total_size)
                
    elapsed = time.time() - start
    size_mb = os.path.getsize(WEIGHTS_PATH) / (1024 * 1024)
    print(f"\nDownload completed in {elapsed:.2f}s! File size: {size_mb:.2f} MB")

    # Verify with Ultralytics
    try:
        from ultralytics import YOLO
        model = YOLO(WEIGHTS_PATH)
        print("Ultralytics YOLO successfully loaded weights! Model classes:", model.names)
    except Exception as e:
        print(f"Verification notice: {e}")

if __name__ == "__main__":
    main()
