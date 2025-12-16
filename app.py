import streamlit as st
from PIL import Image
import requests
import base64
from io import BytesIO

API_URL = "https://piano-inference-production.up.railway.app/predict"

st.title("🎹 Piano Keyboard and Chord Prediction")
uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

def decode_image(b64):
    return Image.open(BytesIO(base64.b64decode(b64)))

if uploaded:
    pil_img = Image.open(uploaded).convert("RGB")
    st.image(pil_img, caption="Original Image", width=600)

    img_bytes = BytesIO()
    pil_img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    with st.spinner("Sending image to backend for prediction..."):
        files = {"file": ("image.png", img_bytes, "image/png")}
        response = requests.post(API_URL, files=files)

    if response.status_code != 200:
        st.error(f"Error from backend: {response.text}")
    else:
        data = response.json()

        if "error" in data:
            st.error(data["error"])
        else:
            # Display images
            st.subheader("Detected Keyboard")
            st.image(decode_image(data["images"]["boxed"]), caption="Bounding Box")

            st.subheader("Cropped Keyboard")
            st.image(decode_image(data["images"]["cropped"]), caption="Cropped Image")

            # Display predictions
            st.subheader("Top 3 Predictions")
            for p in data["predictions"]["top_3"]:
                st.success(f"{p['chord']} ({p['note_name']}) — {p['score']:.2f}")

            st.subheader("Other Possible Chords")
            for p in data["predictions"]["lesser_7"]:
                st.write(f"{p['chord']} ({p['note_name']}) — {p['score']:.2f}")
