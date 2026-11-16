"""
SmartRoad AI — Storage Service
Handles secure image uploads, validation, and file persistence.
"""

import os
import uuid
from typing import Dict, Any, Tuple, Optional
from PIL import Image

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "uploads")
ANNOTATED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "annotated")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(ANNOTATED_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB limit

def validate_and_save_upload(
    file_bytes: bytes,
    original_filename: str
) -> Tuple[bool, str, Optional[str]]:
    """
    Validates file extension, size, and image integrity,
    then persists securely with randomized UUID filename.
    Returns: (success: bool, message_or_path: str, relative_path: Optional[str])
    """
    # 1. File size check
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        return False, f"File exceeds maximum allowed size ({MAX_FILE_SIZE_BYTES // (1024*1024)}MB).", None

    # 2. Extension check
    _, ext = os.path.splitext(original_filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '{ext}'. Allowed: JPG, PNG, WEBP.", None

    # 3. Image integrity verification
    import io
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()
        # Re-open after verify() closes image
        img = Image.open(io.BytesIO(file_bytes))
    except Exception as e:
        return False, f"Corrupted or invalid image file: {str(e)}", None

    # 4. Safe unique filename
    safe_name = f"road_{uuid.uuid4().hex[:12]}{ext}"
    target_path = os.path.join(UPLOAD_DIR, safe_name)
    
    # Save optimized copy
    img.save(target_path, quality=90, optimize=True)
    relative_path = os.path.join("assets", "uploads", safe_name).replace("\\", "/")

    return True, target_path, relative_path

def save_annotated_image(img: Image.Image, base_filename: str = "detection") -> Tuple[str, str]:
    """Saves AI annotated image to assets/annotated/."""
    safe_name = f"annotated_{uuid.uuid4().hex[:12]}.jpg"
    target_path = os.path.join(ANNOTATED_DIR, safe_name)
    img.save(target_path, "JPEG", quality=90)
    relative_path = os.path.join("assets", "annotated", safe_name).replace("\\", "/")
    return target_path, relative_path
