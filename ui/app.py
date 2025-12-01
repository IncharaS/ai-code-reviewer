import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")

if not BACKEND_URL.endswith("/review"):
    BACKEND_URL = BACKEND_URL.rstrip("/") + "/review"

st.title("AI Code Reviewer")

uploaded_file = st.file_uploader("Upload a .py file", type=["py"])

if uploaded_file:
    with st.spinner("Reviewing code..."):
        files = {"file": uploaded_file}
        try:
            resp = requests.post(BACKEND_URL, files=files)
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
            st.stop()

    if resp.status_code == 200:
        data = resp.json()
        st.success("Review completed!")
        st.write(data.get("review", "No review text returned"))
    else:
        st.error("Backend error")
        st.write(resp.text)
