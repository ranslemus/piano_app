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

    # Convert image to bytes for POST
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
            st.image(decode_image(data["images"]["boxed"]), caption="Bounding Box on Original Image")

            st.subheader("Cropped Keyboard")
            st.image(decode_image(data["images"]["cropped"]), caption="Cropped Keyboard Image")

            # Display top 3 notes
            st.subheader("Top 3 Notes")
            st.write(", ".join(data["top_notes"]))

            # Display predicted chord
            st.subheader("Predicted Chord")
            st.success(f"{data['predicted_chord']} (Score: {data['score']:.2f})")

            # Display lesser notes
            st.subheader("Other Possible Notes")
            st.write(", ".join(data["lesser_notes"]))
