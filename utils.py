import fitz
from PIL import Image, ImageOps
import io
import os

# -----------------------------
# FINAL SIZE (400 DPI)
# -----------------------------
CARD_W = 1386
CARD_H = 898


# -----------------------------
# NO-CUT SAFE RESIZE (IMPORTANT)
# -----------------------------
def safe_fit(img, target_w, target_h):

    # Convert to RGB (safe for all PDFs)
    img = img.convert("RGB")

    # Fit image INSIDE target size WITHOUT cropping
    img = ImageOps.contain(img, (target_w, target_h), Image.Resampling.LANCZOS)

    # Create blank white canvas (final card size)
    canvas = Image.new("RGB", (target_w, target_h), (255, 255, 255))

    # Center the image
    x = (target_w - img.width) // 2
    y = (target_h - img.height) // 2

    canvas.paste(img, (x, y))

    return canvas


# -----------------------------
# PROCESS ID CARDS
# -----------------------------
def process_id_cards(pdf_path, output_folder):

    os.makedirs(output_folder, exist_ok=True)

    doc = fitz.open(pdf_path)
    total_pairs = len(doc) // 2

    for i in range(total_pairs):

        pair = i + 1
        front_index = i * 2
        back_index = i * 2 + 1

        try:
            # -------- FRONT --------
            front_pix = doc[front_index].get_pixmap(dpi=400)
            front_img = Image.open(io.BytesIO(front_pix.tobytes()))

            front_img = safe_fit(front_img, CARD_W, CARD_H)

            front_img.save(
                os.path.join(output_folder, f"{pair}A.jpg"),
                "JPEG",
                quality=95
            )

            # -------- BACK --------
            back_pix = doc[back_index].get_pixmap(dpi=400)
            back_img = Image.open(io.BytesIO(back_pix.tobytes()))

            back_img = safe_fit(back_img, CARD_W, CARD_H)

            back_img.save(
                os.path.join(output_folder, f"{pair}B.jpg"),
                "JPEG",
                quality=95
            )

        except Exception as e:
            print(f"Error processing ID {pair}: {e}")

    print("✅ Completed without side cutting")
