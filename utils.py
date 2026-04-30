import fitz
from PIL import Image
import io
import os

# FINAL CARD SIZE (400 DPI)
CARD_W = 1386
CARD_H = 898


# ---------------- SMART CROP (NO DISTORTION) ----------------
def smart_crop(img, target_w, target_h):
    w, h = img.size
    target_ratio = target_w / target_h
    current_ratio = w / h

    if current_ratio > target_ratio:
        # crop sides
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        # crop top/bottom
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    return img.resize((target_w, target_h), Image.Resampling.LANCZOS)


# ---------------- MAIN PROCESS ----------------
def process_id_cards(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    doc = fitz.open(pdf_path)

    total_pairs = len(doc) // 2

    for i in range(total_pairs):
        pair = i + 1
        front = i * 2
        back = i * 2 + 1

        try:
            # FRONT
            pix = doc[front].get_pixmap(dpi=400)
            img = Image.open(io.BytesIO(pix.tobytes()))
            img = smart_crop(img, CARD_W, CARD_H)

            img.convert("RGB").save(
                f"{output_folder}/{pair}A.jpg",
                "JPEG",
                quality=95
            )

            # BACK
            pix = doc[back].get_pixmap(dpi=400)
            img = Image.open(io.BytesIO(pix.tobytes()))
            img = smart_crop(img, CARD_W, CARD_H)

            img.convert("RGB").save(
                f"{output_folder}/{pair}B.jpg",
                "JPEG",
                quality=95
            )

        except Exception as e:
            print(f"Error processing ID {pair}: {e}")

    print("✅ All ID cards processed successfully")
