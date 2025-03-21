import os
import streamlit as st
import base64


def get_sample_transcripts():
    """Return a list of sample transcript files from the setup directory."""
    sample_dir = os.path.join(os.path.dirname(__file__), "setup", "sample_transcripts")
    if os.path.exists(sample_dir):
        return [f for f in sorted(os.listdir(sample_dir)) if f.endswith('.txt')]
    return []


def get_file_download_link(file_path, file_name):
    """Generate a download link for a file."""
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{file_name}">{file_name}</a>'
    return href


def display_sample_transcripts():
    """Display sample transcripts with download links."""
    st.subheader("Sample Transcripts")

    samples = get_sample_transcripts()
    if not samples:
        st.info("No sample transcripts available.")
        return

    st.write("Download sample transcripts to test the application:")

    for sample in samples:
        file_path = os.path.join(os.path.dirname(__file__), "setup", "sample_transcripts", sample)
        st.markdown(get_file_download_link(file_path, sample), unsafe_allow_html=True)
