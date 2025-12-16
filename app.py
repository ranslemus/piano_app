import streamlit as st
import numpy as np
from PIL import Image
import requests
import io

API_URL = "https://piano-inference-production.up.railway.app/predict"

st.set_page_config(page_title="Piano Chord Detector", layout="centered")
st.title("🎹 Piano Keyboard and Chord Prediction")

uploaded = st.file_uploader(
    "Upload a piano keyboard image",
    type=["jpg", "jpeg", "png"]
)

if uploaded:
    pil_img = Image.open(uploaded).convert("RGB")
    st.image(pil_img, caption="Original Image", use_container_width=True)

    img_bytes = io.BytesIO()
    pil_img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    with st.spinner("Sending image to backend for prediction..."):
        try:
            response = requests.post(
                API_URL,
                files={"file": ("image.png", img_bytes, "image/png")},
                timeout=60  # important for cold starts
            )
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Backend not reachable:\n{e}")
            st.stop()

    if response.status_code != 200:
        st.error(f"❌ Backend error ({response.status_code}):\n{response.text}")
        st.stop()

    data = response.json()

    if "error" in data:
        st.error(f"⚠️ {data['error']}")
    else:
        st.subheader("🎼 Prediction Results")
        st.write("**Top Notes (indices):**", data["top_notes"])
        st.write("**Note Names:**", data["note_names"])
        st.success(
            f"🎵 **Predicted Chord:** {data['predicted_chord']} "
            f"(Score: {data['score']:.2f})"
        )

        if "other_notes" in data:
            st.subheader("Other Top Notes")
            st.write(data["other_notes"])
