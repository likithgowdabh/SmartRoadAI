# SmartRoad AI — YOLO11 Pothole Detector Training Guide

## 1. Model Architecture

SmartRoad AI uses **YOLO11n (Nano)**:
- **Parameter Count:** ~2.6M parameters
- **FLOPs:** 6.5 GFLOPs
- **Inference Latency:** ~15–30 ms on CPU, < 5 ms on GPU
- **Target Output:** High precision bounding boxes for potholes (`D40`) with calibrated confidence scores.

## 2. Option A: Free Cloud GPU Training (Recommended)

Google Colab provides a free NVIDIA T4 GPU that trains YOLO11n on the RDD2022 dataset in approximately 15–20 minutes.

### Step-by-Step Instructions:
1. Open Google Colab ([colab.research.google.com](https://colab.research.google.com)).
2. Upload the included notebook: `training/smartroad_yolo11_colab.ipynb`.
3. In Colab menu, select: **Runtime → Change runtime type → T4 GPU → Save**.
4. Run all cells sequentially:
   - Cell 1: Verifies GPU (`nvidia-smi`)
   - Cell 2: Installs `ultralytics`
   - Cell 3: Downloads `RDD2022_India.zip` (~500 MB)
   - Cell 4: Converts Pascal VOC XML to YOLO format for class `D40`
   - Cell 5: Executes training for 40 epochs with `patience=10`
   - Cell 6: Evaluates on test split (Precision, Recall, mAP50, mAP50-95)
   - Cell 7: Downloads the resulting `best.pt` file
5. Rename the downloaded file to `pothole_best.pt` and place it in your local workspace:
   ```
   SmartRoad-AI/models/pothole_best.pt
   ```
6. Reload the SmartRoad AI app — the status pill immediately switches to **"YOLO11 Custom Pothole Weights Active"**!

## 3. Option B: Local Training (Requires GPU or CPU Time)

If you have a local NVIDIA GPU with CUDA:
```bash
python training/train_yolo.py --data datasets/rdd2022_potholes/pothole_dataset.yaml --epochs 50 --batch 16 --device 0
```

On CPU:
```bash
python training/train_yolo.py --data datasets/rdd2022_potholes/pothole_dataset.yaml --epochs 25 --batch 8 --device cpu
```

## 4. Evaluation Metrics

Trained weights should achieve the following benchmark thresholds on the RDD2022 D40 test split:
- **Precision (P):** $\ge 0.72$
- **Recall (R):** $\ge 0.68$
- **mAP@50:** $\ge 0.74$
- **mAP@50-95:** $\ge 0.45$

SmartRoad AI displays verified empirical metrics from model evaluation, strictly avoiding fabricated numbers.
