import streamlit as st
from PIL import Image
import requests
import base64
from io import BytesIO

API_URL = "https://piano-inference-production.up.railway.app/predict"

st.title("🎹 Piano Keyboard and Chord Prediction")
uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

def decode_image(b64_str):
    return Image.open(BytesIO(base64.b64decode(b64_str)))

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
            # Show images from backend
            if "images" in data:
                st.subheader("Detected Keyboard with Bounding Box")
                st.image(decode_image(data["images"]["boxed"]), caption="Bounding Box")

                st.subheader("Cropped Keyboard")
                st.image(decode_image(data["images"]["cropped"]), caption="Cropped Image")

            # Show predictions
            top_notes = data.get("top_notes", [])
            predicted_chord = data.get("predicted_chord", "")
            chord_score = data.get("score", 0.0)
            lesser_notes = data.get("lesser_notes", [])

            st.subheader("Top 3 Notes")
            for note in top_notes:
                st.success(note)

            st.subheader("Predicted Chord")
            st.success(f"{predicted_chord} — Score: {chord_score:.2f}")

            st.subheader("7 Lesser Notes")
            for note in lesser_notes:
                st.write(note)
