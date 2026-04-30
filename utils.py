import fitz  # PyMuPDF
from PIL import Image, ImageOps
import io
import os
import re


# -----------------------------
# FINAL CARD SIZE (400 DPI)
# -----------------------------
CARD_W = 1386
CARD_H = 898


# -----------------------------
# SAFE FIT (NO CUT)
# -----------------------------
def safe_fit(img, target_w, target_h):

    img = img.convert("RGB")

    # Resize inside without cropping
    img = ImageOps.contain(img, (target_w, target_h), Image.Resampling.LANCZOS)

    # Create white background
    canvas = Image.new("RGB", (target_w, target_h), (255, 255, 255))

    # Center image
    x = (target_w - img.width) // 2
    y = (target_h - img.height) // 2

    canvas.paste(img, (x, y))

    return canvas


# -----------------------------
# PROCESS ID CARDS
# -----------------------------
def process_id_cards(pdf_path, output_folder):

    os.makedirs(output_folder, exist_ok=True)

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"❌ Error opening PDF: {e}")
        return

    # -----------------------------
    # 🔥 Extract LAST number from filename (IMPORTANT FIX)
    # -----------------------------
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    numbers = re.findall(r'\d+', pdf_name)

    if numbers:
        pdf_number = numbers[-1]   # take LAST number
    else:
        pdf_number = "0"

    total_pairs = len(doc) // 2

    if total_pairs == 0:
        print(f"⚠️ No ID pairs found in {pdf_name}")
        return

    # -----------------------------
    # PROCESS EACH ID
    # -----------------------------
    for i in range(total_pairs):

        id_index = i + 1
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

            print(f"✅ PDF {pdf_number} → ID {id_index} done")

        except Exception as e:
            print(f"❌ Error in PDF {pdf_number}, ID {id_index}: {e}")

    print(f"🎉 Completed PDF {pdf_number}")
