# Executed in a folder, converts everything to webp.

import os
from PIL import Image
import piexif

for filepath in os.listdir(os.getcwd()):
    full_path = os.path.join(os.getcwd(), filepath)
    if not os.path.isfile(full_path):
        continue
    prefix, _ = os.path.splitext(filepath)

    try:
        image = Image.open(full_path)
        if "exif" in image.info:
            piexif.remove(full_path)
        image.save(prefix + ".webp", format="WebP", lossless=False, quality=100)

    except Exception as e:
        print(f"Failed to process '{filepath}': {e}")
