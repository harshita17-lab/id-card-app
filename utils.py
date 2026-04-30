import fitz
from PIL import Image, ImageOps
import io
import os


CARD_W = 1386
CARD_H = 898


# ---------------- SAFE FIT (NO CUT) ----------------
def safe_fit(img, target_w, target_h):

    img = img.convert("RGB")

    img = ImageOps.contain(img, (target_w, target_h), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (target_w, target_h), (255, 255, 255))

    x = (target_w - img.width) // 2
    y = (target_h - img.height) // 2

    canvas.paste(img, (x, y))

    return canvas


# ---------------- PROCESS SINGLE PDF ----------------
def process_id_cards(pdf_path, output_folder):

    os.makedirs(output_folder, exist_ok=True)

    doc = fitz.open(pdf_path)

    # extract PDF number from filename (e.g., "2.pdf" → 2)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    pdf_number = pdf_name  # keeps "1", "2", etc.

    total_pairs = len(doc) // 2

    for i in range(total_pairs):

        id_index = i + 1  # 1-based inside each PDF

        front_index = i * 2
        back_index = i * 2 + 1

        try:
            # -------- FRONT --------
            front_pix = doc[front_index].get_pixmap(dpi=400)
            front_img = Image.open(io.BytesIO(front_pix.tobytes()))
            front_img = safe_fit(front_img, CARD_W, CARD_H)

            front_img.save(
                os.path.join(output_folder, f"{pdf_number}_{id_index}F.jpg"),
                "JPEG",
                quality=95
            )

            # -------- BACK --------
            back_pix = doc[back_index].get_pixmap(dpi=400)
            back_img = Image.open(io.BytesIO(back_pix.tobytes()))
            back_img = safe_fit(back_img, CARD_W, CARD_H)

            back_img.save(
                os.path.join(output_folder, f"{pdf_number}_{id_index}B.jpg"),
                "JPEG",
                quality=95
            )

        except Exception as e:
            print(f"Error processing ID {id_index} in PDF {pdf_number}: {e}")

    print(f"✅ Completed PDF {pdf_number}")
