import streamlit as st
import os
import zipfile
from utils import process_id_cards

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output_cards"
ZIP_FILE = "id_cards.zip"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


st.title("🆔 ID Card Generator")

uploaded_file = st.file_uploader("Upload ID Card PDF", type=["pdf"])

if uploaded_file:

    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("File uploaded successfully!")

    if st.button("Generate ID Cards"):

        # 🧹 clear old output
        for f in os.listdir(OUTPUT_FOLDER):
            os.remove(os.path.join(OUTPUT_FOLDER, f))

        with st.spinner("Processing..."):
            process_id_cards(file_path, OUTPUT_FOLDER)

        # create zip
        with zipfile.ZipFile(ZIP_FILE, "w") as zipf:
            for file in os.listdir(OUTPUT_FOLDER):
                zipf.write(os.path.join(OUTPUT_FOLDER, file), file)

        st.success("Done!")

        with open(ZIP_FILE, "rb") as f:
            st.download_button(
                "Download ID Cards ZIP",
                f,
                file_name="id_cards.zip"
            )
