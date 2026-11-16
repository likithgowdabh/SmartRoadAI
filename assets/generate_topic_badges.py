import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

os.makedirs("assets", exist_ok=True)

def create_blue_vision_badge():
    size = (360, 220)
    img = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Soft Blue gradient background rounded card
    # #EBF5FF to #D6EBFF
    draw.rounded_rectangle([(10, 10), (350, 210)], radius=20, fill=(235, 245, 255, 255), outline=(0, 113, 227, 80), width=2)
    
    # Glowing scan grid
    for x in range(30, 340, 25):
        draw.line([(x, 30), (x, 190)], fill=(0, 113, 227, 25), width=1)
    for y in range(30, 200, 25):
        draw.line([(30, y), (330, y)], fill=(0, 113, 227, 25), width=1)
        
    # Blue Central Microchip / Camera Reticle
    cx, cy = 180, 110
    draw.rounded_rectangle([(cx - 40, cy - 40), (cx + 40, cy + 40)], radius=12, fill=(0, 113, 227, 255))
    draw.rounded_rectangle([(cx - 30, cy - 30), (cx + 30, cy + 30)], radius=8, fill=(255, 255, 255, 255))
    draw.rounded_rectangle([(cx - 20, cy - 20), (cx + 20, cy + 20)], radius=6, fill=(0, 113, 227, 255))
    
    # Corner brackets (Pothole Bounding Box)
    b_color = (0, 119, 237)
    l = 24
    # Top-Left
    draw.line([(40, 40), (40 + l, 40)], fill=b_color, width=4)
    draw.line([(40, 40), (40, 40 + l)], fill=b_color, width=4)
    # Bottom-Right
    draw.line([(320, 180), (320 - l, 180)], fill=b_color, width=4)
    draw.line([(320, 180), (320, 180 - l)], fill=b_color, width=4)
    
    img.save("assets/feat_vision_blue.png", "PNG")

def create_skin_priority_badge():
    size = (360, 220)
    img = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Warm Skin / Amber / Peach gradient rounded card
    # Base #FFF3E6
    draw.rounded_rectangle([(10, 10), (350, 210)], radius=20, fill=(255, 243, 230, 255), outline=(218, 130, 40, 80), width=2)
    
    cx, cy = 180, 110
    # Multi-factor radial dial
    draw.arc([(cx - 65, cy - 65), (cx + 65, cy + 65)], start=140, end=400, fill=(230, 190, 160), width=10)
    # Active high-priority arc (Skin warm amber #D97706)
    draw.arc([(cx - 65, cy - 65), (cx + 65, cy + 65)], start=140, end=330, fill=(217, 119, 6), width=12)
    
    # Inner central hub
    draw.ellipse([(cx - 30, cy - 30), (cx + 30, cy + 30)], fill=(217, 119, 6))
    draw.ellipse([(cx - 18, cy - 18), (cx + 18, cy + 18)], fill=(255, 255, 255))
    
    # Needle
    draw.line([(cx, cy), (cx + 38, cy - 28)], fill=(180, 80, 0), width=4)
    
    # Priority Equation Tokens
    draw.rounded_rectangle([(30, 155), (105, 185)], radius=6, fill=(245, 215, 190))
    draw.rounded_rectangle([(255, 155), (330, 185)], radius=6, fill=(245, 215, 190))
    
    img.save("assets/feat_priority_skin.png", "PNG")

def create_green_dispatch_badge():
    size = (360, 220)
    img = Image.new("RGBA", size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Soft Emerald Green background rounded card
    # #EAF6ED to #D4EEDC
    draw.rounded_rectangle([(10, 10), (350, 210)], radius=20, fill=(234, 246, 237, 255), outline=(36, 138, 61, 80), width=2)
    
    cx, cy = 180, 105
    # Smooth road pavement band
    draw.polygon([(40, 180), (320, 180), (250, 60), (110, 60)], fill=(200, 230, 210))
    # Green center line
    draw.line([(180, 60), (180, 180)], fill=(36, 138, 61), width=4)
    
    # Central Municipal Seal Badge
    draw.ellipse([(cx - 40, cy - 40), (cx + 40, cy + 40)], fill=(36, 138, 61))
    draw.ellipse([(cx - 32, cy - 32), (cx + 32, cy + 32)], fill=(255, 255, 255))
    
    # Checkmark inside green seal
    draw.line([(cx - 16, cy), (cx - 4, cy + 12)], fill=(36, 138, 61), width=5)
    draw.line([(cx - 4, cy + 12), (cx + 16, cy - 10)], fill=(36, 138, 61), width=5)
    
    img.save("assets/feat_dispatch_green.png", "PNG")

create_blue_vision_badge()
create_skin_priority_badge()
create_green_dispatch_badge()
print("Topic badges in blue, skin, and green color spaces generated.")
