import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

os.makedirs("assets", exist_ok=True)

def generate_road_image(filename, annotated_filename, num_potholes=2):
    w, h = 640, 480
    np.random.seed(42 + num_potholes)
    # Base asphalt texture (gray with noise)
    noise = np.random.normal(90, 15, (h, w)).clip(40, 140).astype(np.uint8)
    base = Image.fromarray(noise, mode="L").convert("RGB")
    draw = ImageDraw.Draw(base)

    # Road lane markings
    draw.line([(w // 2, 0), (w // 2, h)], fill=(185, 185, 155), width=6)

    boxes = []
    for i in range(num_potholes):
        cx = int(w * (0.32 + 0.35 * (i % 2)))
        cy = int(h * (0.35 + 0.3 * (i // 2)))
        rx = np.random.randint(45, 75)
        ry = np.random.randint(35, 60)
        
        points = []
        for angle in np.linspace(0, 2 * np.pi, 16, endpoint=False):
            r = (rx if np.cos(angle)**2 > 0.5 else ry) * np.random.uniform(0.75, 1.25)
            px = int(cx + r * np.cos(angle))
            py = int(cy + r * np.sin(angle))
            points.append((px, py))
        draw.polygon(points, fill=(28, 28, 30))
        boxes.append((cx - rx - 12, cy - ry - 12, cx + rx + 12, cy + ry + 12))

    base = base.filter(ImageFilter.GaussianBlur(radius=0.7))
    base.save(filename, "JPEG", quality=92)

    # Annotated version
    annotated = base.copy()
    ann_draw = ImageDraw.Draw(annotated)
    for b in boxes:
        x1, y1, x2, y2 = b
        ann_draw.rectangle([x1, y1, x2, y2], outline=(0, 113, 227), width=2)
        ann_draw.rectangle([x1, max(0, y1 - 20), x1 + 105, y1], fill=(0, 113, 227))
        ann_draw.text((x1 + 4, max(2, y1 - 18)), "pothole 92%", fill=(255, 255, 255))
    annotated.save(annotated_filename, "JPEG", quality=92)

for i in range(1, 5):
    generate_road_image(f"assets/sample_pothole_{i}.jpg", f"assets/sample_annotated_{i}.jpg", num_potholes=(i % 3 + 1))

print("Sample road damage assets generated successfully.")
