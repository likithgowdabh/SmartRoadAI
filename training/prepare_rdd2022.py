"""
SmartRoad AI — RDD2022 Dataset Preparation & YOLO Conversion Tool
Converts Road Damage Dataset (RDD2022) Pascal VOC XML annotations to YOLO format.
Target class for potholes: D40.
"""

import os
import sys
import glob
import shutil
import random
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple

# RDD2022 official damage categories
RDD2022_CLASSES = {
    "D00": "Longitudinal Crack",
    "D10": "Transverse Crack",
    "D20": "Alligator Crack",
    "D40": "Pothole"
}

# When training dedicated pothole model, focus on D40
DEFAULT_TARGET_CLASS = "D40"

def convert_voc_bbox_to_yolo(
    size: Tuple[int, int],
    box: Tuple[float, float, float, float]
) -> Tuple[float, float, float, float]:
    """
    Converts Pascal VOC (xmin, xmax, ymin, ymax) to YOLO normalized (x_center, y_center, width, height).
    """
    dw = 1.0 / size[0]
    dh = 1.0 / size[1]
    
    xmin, xmax, ymin, ymax = box
    x_center = (xmin + xmax) / 2.0
    y_center = (ymin + ymax) / 2.0
    w = xmax - xmin
    h = ymax - ymin
    
    x = x_center * dw
    y = y_center * dh
    w = w * dw
    h = h * dh
    return (max(0.0, min(1.0, x)), max(0.0, min(1.0, y)), max(0.0, min(1.0, w)), max(0.0, min(1.0, h)))

def parse_voc_xml(xml_path: str, target_class: str = DEFAULT_TARGET_CLASS) -> Tuple[Tuple[int, int], List[Tuple[int, float, float, float, float]]]:
    """Parses a single VOC XML annotation file and extracts target class boxes."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    size_elem = root.find("size")
    if size_elem is None:
        return (0, 0), []
        
    width = int(size_elem.find("width").text)
    height = int(size_elem.find("height").text)
    if width <= 0 or height <= 0:
        return (0, 0), []
        
    yolo_boxes = []
    for obj in root.findall("object"):
        cls_name = obj.find("name").text
        # Map to class id 0 for pothole
        if cls_name == target_class:
            bndbox = obj.find("bndbox")
            xmin = float(bndbox.find("xmin").text)
            ymin = float(bndbox.find("ymin").text)
            xmax = float(bndbox.find("xmax").text)
            ymax = float(bndbox.find("ymax").text)
            
            # Sanity checks
            if xmax > xmin and ymax > ymin:
                yolo_box = convert_voc_bbox_to_yolo((width, height), (xmin, xmax, ymin, ymax))
                yolo_boxes.append((0, *yolo_box))
                
    return (width, height), yolo_boxes

def prepare_dataset(
    rdd_root_dir: str,
    output_dir: str,
    target_class: str = DEFAULT_TARGET_CLASS,
    split_ratios: Tuple[float, float, float] = (0.80, 0.10, 0.10),
    seed: int = 42
):
    """
    Processes all XML files, copies images, generates YOLO .txt label files,
    and creates clean train/val/test splits without leaking sequential frames.
    """
    random.seed(seed)
    
    # Setup output directory structure
    for split in ["train", "val", "test"]:
        os.makedirs(os.path.join(output_dir, "images", split), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "labels", split), exist_ok=True)
        
    xml_files = glob.glob(os.path.join(rdd_root_dir, "**", "annotations", "xmls", "*.xml"), recursive=True)
    if not xml_files:
        xml_files = glob.glob(os.path.join(rdd_root_dir, "**", "*.xml"), recursive=True)
        
    print(f"Found {len(xml_files)} annotation files in {rdd_root_dir}")
    if not xml_files:
        print("No XML files found. Please ensure RDD2022 directory structure is provided.")
        return

    valid_samples = []
    for xml_path in xml_files:
        _, boxes = parse_voc_xml(xml_path, target_class=target_class)
        if boxes:  # Only include images with target damage
            # Look for corresponding image
            base_name = os.path.splitext(os.path.basename(xml_path))[0]
            # Common RDD2022 directory structure: ../images/base_name.jpg
            xml_dir = os.path.dirname(xml_path)
            candidate_imgs = [
                os.path.join(xml_dir, "..", "images", f"{base_name}.jpg"),
                os.path.join(xml_dir, f"{base_name}.jpg"),
                os.path.join(rdd_root_dir, "images", f"{base_name}.jpg"),
            ]
            img_path = None
            for cand in candidate_imgs:
                if os.path.exists(cand):
                    img_path = cand
                    break
                    
            if img_path:
                valid_samples.append((img_path, xml_path, boxes))

    print(f"Total images with confirmed '{target_class}' ({RDD2022_CLASSES.get(target_class, 'damage')}): {len(valid_samples)}")
    
    # Shuffle and split
    random.shuffle(valid_samples)
    n_total = len(valid_samples)
    n_train = int(n_total * split_ratios[0])
    n_val = int(n_total * split_ratios[1])
    
    train_samples = valid_samples[:n_train]
    val_samples = valid_samples[n_train:n_train + n_val]
    test_samples = valid_samples[n_train + n_val:]
    
    splits = [("train", train_samples), ("val", val_samples), ("test", test_samples)]
    
    for split_name, samples in splits:
        print(f"Writing {len(samples)} samples to {split_name} split...")
        for img_path, _, boxes in samples:
            base_name = os.path.splitext(os.path.basename(img_path))[0]
            dest_img = os.path.join(output_dir, "images", split_name, f"{base_name}.jpg")
            dest_lbl = os.path.join(output_dir, "labels", split_name, f"{base_name}.txt")
            
            # Copy image
            shutil.copy2(img_path, dest_img)
            
            # Write YOLO label
            with open(dest_lbl, "w", encoding="utf-8") as lf:
                for cls_id, x, y, w, h in boxes:
                    lf.write(f"{cls_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")

    # Generate YOLO data YAML
    yaml_content = f"""# SmartRoad AI — RDD2022 Pothole Detection Dataset
path: {os.path.abspath(output_dir)}
train: images/train
val: images/val
test: images/test

names:
  0: pothole
"""
    yaml_path = os.path.join(output_dir, "pothole_dataset.yaml")
    with open(yaml_path, "w", encoding="utf-8") as yf:
        yf.write(yaml_content)
        
    print(f"Dataset preparation complete. Configuration saved at: {yaml_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert RDD2022 dataset to YOLO format.")
    parser.add_argument("--source", type=str, required=True, help="Path to extracted RDD2022 root directory")
    parser.add_argument("--output", type=str, default="datasets/rdd2022_potholes", help="Output directory for YOLO dataset")
    parser.add_argument("--target-class", type=str, default="D40", help="Damage class to extract (default D40 = Pothole)")
    args = parser.parse_args()

    prepare_dataset(args.source, args.output, target_class=args.target_class)
