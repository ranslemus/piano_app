import streamlit as st
from PIL import Image
import requests
import base64
from io import BytesIO

API_URL = "https://piano-inference-production.up.railway.app/predict"

st.set_page_config(page_title="Piano Note & Chord Detector", layout="centered")
st.title("🎹 Piano Note & Chord Detection")

uploaded = st.file_uploader("Upload a piano keyboard image", type=["jpg", "jpeg", "png"])

def decode_image(b64_str):
    return Image.open(BytesIO(base64.b64decode(b64_str)))

if uploaded:
    pil_img = Image.open(uploaded).convert("RGB")
    st.image(pil_img, caption="Original Image", use_container_width=True)

    # Convert image to bytes
    img_bytes = BytesIO()
    pil_img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    with st.spinner("Analyzing keyboard..."):
        files = {"file": ("image.png", img_bytes, "image/png")}
        response = requests.post(API_URL, files=files)

    if response.status_code != 200:
        st.error(f"Backend error: {response.text}")
    else:
        data = response.json()

        if "error" in data:
            st.error(data["error"])
        else:
            # ---- Images ----
            st.subheader("🎯 Detected Keyboard")
            st.image(
                decode_image(data["images"]["boxed"]),
                caption="Keyboard Bounding Box",
                use_container_width=True
            )

            st.subheader("✂️ Cropped Keyboard")
            st.image(
                decode_image(data["images"]["cropped"]),
                caption="Keyboard Crop",
                use_container_width=True
            )

            # ---- Top 10 Notes ----
            st.subheader("🎼 Detected Notes (Top 10)")
            for note in data["detected_notes_top_10"]:
                st.write(
                    f"• **{note['note_name']}** "
                    f"(index: `{note['note_index']}`) "
                    f"— confidence: `{note['confidence']:.3f}`"
                )

            # ---- Predicted Chord ----
            st.subheader("🎵 Predicted Chord")
            st.success(
                f"{data['predicted_chord']} "
                f"(confidence: {data['chord_score']:.2f})"
            )
