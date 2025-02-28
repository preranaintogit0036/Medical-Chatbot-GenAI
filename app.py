# Import necessary modules
import sys
import subprocess

# Check if google-generativeai is installed, if not, install it
try:
    import google.generativeai as genai
except ModuleNotFoundError:
    subprocess.run([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai
import streamlit as st
from pathlib import Path
import google.generativeai as genai

from Medical_Chatbot_GenAI.api_key import api_key  # Ensure api_key.py is correctly set up

# Set Streamlit page config (MUST be the first command)
st.set_page_config(page_title="SwastiCare", page_icon="🩺")

# Configure GenAI with API key
genai.configure(api_key=api_key)

# Set up the model configuration
generation_config = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Function to upload files to Gemini
def upload_to_gemini(file_path, mime_type):
    """Uploads the given file to Gemini and returns the file object."""
    if not Path(file_path).exists():
        st.error("⚠️ File not found. Please upload a valid image.")
        return None
    file = genai.upload_file(file_path, mime_type=mime_type)
    st.success(f"✅ Uploaded file '{file.display_name}' as: {file.uri}")
    return file

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

# Set the logo
st.image("Swasti_Bot_logo.png", width=150)

# Set the title and subtitle
st.title("SwastiCare: SympSolver 🩺")
st.subheader("An application that helps users identify medical images")

# File uploader
uploaded_file = st.file_uploader("Upload the medical image for analysis", type=["png", "jpg", "jpeg"])

# Custom styling for the button
st.markdown("""
    <style>
        div.stButton > button {
            background-color: #FFD700;
            color: black;
            font-weight: bold;
            border-radius: 8px;
            padding: 12px;
            font-size: 16px;
            transition: 0.3s;
            border: none;
            cursor: pointer;
        }
        div.stButton > button:hover {
            background-color: #FFAA00;
            transform: scale(1.08);
        }
    </style>
""", unsafe_allow_html=True)

# Submit button
if st.button("🩺 Generate Analysis"):
    if uploaded_file is not None:
        # Save uploaded file to a temporary location
        temp_file_path = f"temp_{uploaded_file.name}"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Upload file to Gemini
        file_obj = upload_to_gemini(temp_file_path, mime_type="image/png")

        if file_obj:
            # Start chat session with the uploaded file
            chat_session = model.start_chat(history=[{"role": "user", "parts": [file_obj]}])

            # Send prompt to model
            response = chat_session.send_message("Analyze this medical image and provide a detailed report.")

            # Display response
            st.subheader("📋 Analysis Result:")
            st.write(response.text)

        # Remove temporary file after processing
        Path(temp_file_path).unlink()

    else:
        st.warning("⚠️ Please upload an image before submitting.")
