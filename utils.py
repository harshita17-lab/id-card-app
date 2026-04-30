import fitz  # PyMuPDF
from PIL import Image
import io
import os

# -----------------------------
# FINAL ID CARD SIZE (400 DPI)
# -----------------------------
CARD_WIDTH = 1386
CARD_HEIGHT = 898


# -----------------------------
# SAFE SMART CROP (FIXED)
# prevents right-side cutting
# -----------------------------
def smart_crop(img, target_w, target_h):
    w, h = img.size
    target_ratio = target_w / target_h
    current_ratio = w / h

    # safety margin (fixes edge cutting issue)
    margin = int(min(w, h) * 0.02)  # 2%

    if current_ratio > target_ratio:
        # wider image → crop sides
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2

        left = max(0, left - margin)
        right = min(w, left + new_w + margin)

        img = img.crop((left, 0, right, h))

    else:
        # taller image → crop top/bottom
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2

        top = max(0, top - margin)
        bottom = min(h, top + new_h + margin)

        img = img.crop((0, top, w, bottom))

    return img.resize((target_w, target_h), Image.Resampling.LANCZOS)


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def process_id_cards(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return

    total_pairs = len(doc) // 2

    for i in range(total_pairs):
        pair_num = i + 1
        front_index = i * 2
        back_index = i * 2 + 1

        try:
            # ---------------- FRONT ----------------
            front_pix = doc[front_index].get_pixmap(dpi=400)
            front_img = Image.open(io.BytesIO(front_pix.tobytes()))
            front_img = smart_crop(front_img, CARD_WIDTH, CARD_HEIGHT)

            front_img.convert("RGB").save(
                os.path.join(output_folder, f"{pair_num}A.jpg"),
                "JPEG",
                quality=95
            )

            # ---------------- BACK ----------------
            back_pix = doc[back_index].get_pixmap(dpi=400)
            back_img = Image.open(io.BytesIO(back_pix.tobytes()))
            back_img = smart_crop(back_img, CARD_WIDTH, CARD_HEIGHT)

            back_img.convert("RGB").save(
                os.path.join(output_folder, f"{pair_num}B.jpg"),
                "JPEG",
                quality=95
            )

        except Exception as e:
            print(f"Error processing ID {pair_num}: {e}")

    print("✅ All ID cards processed successfully")
