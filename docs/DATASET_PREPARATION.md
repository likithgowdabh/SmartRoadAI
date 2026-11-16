# SmartRoad AI — RDD2022 Dataset Preparation Guide

## 1. Dataset Overview & Official Source

The **Road Damage Dataset 2022 (RDD2022)** was released as part of the **Crowdsensing-based Road Damage Detection Challenge (CRDDC'2022)** (IEEE BigData Cup) by the Sekilab research group at the University of Tokyo.

- **Official GitHub:** [https://github.com/sekilab/RoadDamageDetector](https://github.com/sekilab/RoadDamageDetector)
- **Official Figshare Archive:** [https://doi.org/10.6084/m9.figshare.21431547](https://doi.org/10.6084/m9.figshare.21431547)
- **License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

## 2. Dataset Size & Breakdown

The dataset contains over **47,420+ images** captured across 6 nations with tens of thousands of labeled damage instances.

| Country Subset | Size | Recommended For | Pothole Density |
| :--- | :--- | :--- | :--- |
| **India (`RDD2022_India.zip`)** | **~502 MB** | **Recommended (Colab & Local)** | High (D40) |
| **Japan (`RDD2022_Japan.zip`)** | **~1.0 GB** | **High Quality Benchmark** | High (D40) |
| **United States (`RDD2022_United_States.zip`)** | ~424 MB | Urban Asphalt Comparison | Moderate |
| **Czech Republic (`RDD2022_Czech.zip`)** | ~245 MB | Fast Prototyping | Moderate |
| **China MotorBike (`RDD2022_China_MotorBike.zip`)** | ~183 MB | Two-Wheeler Camera Angles | High |
| **Norway (`RDD2022_Norway.zip`)** | ~9.9 GB | Large Scale Multi-Lane | Low/Sparse |

> [!TIP]
> For fast, free model training on Google Colab or modest local hardware, download **`RDD2022_India.zip` (~502 MB)** or **`RDD2022_Japan.zip` (~1.0 GB)**. Avoid downloading the entire 12 GB multi-country archive unless training a massive enterprise backbone.

## 3. Damage Categories & Classes

The dataset uses Pascal VOC XML annotations defining four primary road surface categories:

| Class Code | Category Name | Description | Used by SmartRoad AI |
| :--- | :--- | :--- | :--- |
| **`D00`** | Longitudinal Crack | Cracks parallel to the road center line | Secondary |
| **`D10`** | Transverse Crack | Cracks perpendicular to the road center line | Secondary |
| **`D20`** | Alligator Crack | Interconnected fatigue cracking / crocodile skin | Secondary |
| **`D40`** | **Pothole** | **Asphalt cavities, surface breaks, craters** | **Primary (Target Class 0)** |

## 4. Converting Pascal VOC XML to YOLO Format

SmartRoad AI includes an automated conversion and splitting tool: `training/prepare_rdd2022.py`.

### Execution:
```bash
python training/prepare_rdd2022.py --source /path/to/extracted/RDD2022_India --output datasets/rdd2022_potholes --target-class D40
```

### What this does:
1. Scans all XML annotation files.
2. Extracts bounding coordinates for class `D40` (`xmin`, `ymin`, `xmax`, `ymax`).
3. Converts coordinates to normalized YOLO format:
   $$\text{x\_center} = \frac{\text{xmin} + \text{xmax}}{2 \times \text{width}}$$
   $$\text{y\_center} = \frac{\text{ymin} + \text{ymax}}{2 \times \text{height}}$$
   $$\text{width} = \frac{\text{xmax} - \text{xmin}}{\text{width}}$$
   $$\text{height} = \frac{\text{ymax} - \text{ymin}}{\text{height}}$$
4. Creates non-leaking splits (80% Train, 10% Validation, 10% Test).
5. Generates the Ultralytics configuration file: `datasets/rdd2022_potholes/pothole_dataset.yaml`.
