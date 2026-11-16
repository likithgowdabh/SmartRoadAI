"""
SmartRoad AI — YOLO11 Pothole Detection Model Training Script
Trains a custom YOLO11n model using Ultralytics PyTorch framework.
Saves weights directly to models/pothole_best.pt
"""

import os
import sys
import argparse

def train_pothole_model(
    data_yaml: str,
    epochs: int = 50,
    imgsz: int = 640,
    batch: int = 16,
    weights_base: str = "yolo11n.pt",
    output_dir: str = "models",
    device: str = "0"
):
    """Executes YOLO11 training on the custom pothole dataset."""
    try:
        from ultralytics import YOLO
    except ImportError:
        print("ERROR: ultralytics is required for model training. Install via: pip install ultralytics")
        sys.exit(1)

    print(f"--- SmartRoad AI Model Training ---")
    print(f"Base Weights: {weights_base}")
    print(f"Dataset YAML: {data_yaml}")
    print(f"Epochs: {epochs} | Batch: {batch} | Img Size: {imgsz}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Load base architecture
    model = YOLO(weights_base)
    
    # Train
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        patience=12,
        save=True,
        project="runs/detect",
        name="pothole_yolo11",
        exist_ok=True
    )
    
    # Save best weights to models/pothole_best.pt
    best_weights_src = os.path.join("runs", "detect", "pothole_yolo11", "weights", "best.pt")
    target_weights = os.path.join(output_dir, "pothole_best.pt")
    
    if os.path.exists(best_weights_src):
        import shutil
        shutil.copy2(best_weights_src, target_weights)
        print(f"SUCCESS: Best trained weights deployed to: {target_weights}")
    else:
        print(f"Training completed. Check runs/detect/pothole_yolo11/weights/ for output files.")

    # Run validation evaluation
    metrics = model.val()
    print(f"Validation mAP50: {metrics.box.map50:.4f}")
    print(f"Validation mAP50-95: {metrics.box.map:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train custom YOLO11 pothole detector.")
    parser.add_argument("--data", type=str, default="datasets/rdd2022_potholes/pothole_dataset.yaml", help="Path to dataset yaml")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu or 0)")
    args = parser.parse_args()

    train_pothole_model(args.data, epochs=args.epochs, imgsz=args.imgsz, batch=args.batch, device=args.device)
