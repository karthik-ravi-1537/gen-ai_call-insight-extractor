import base64

import streamlit as st
import requests

# Set the backend URL. You can also set this in a secrets.toml file.
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")
API_URL = BACKEND_URL + st.secrets.get("API_PREFIX", "/api/v1")

st.title("Gen-AI Call Insight Extractor")

st.markdown("## Upload Transcript File(s)")

uploaded_file = st.file_uploader(
    "Select the transcript file (TXT)",
    type=["txt"],
    accept_multiple_files=False  # Only one file allowed at a time
)

if st.button("Upload Call Transcript(s)"):
    if not uploaded_file:
        st.warning("No file selected. Please upload a file.")
    else:
        files = [
            ("files", (uploaded_file.name, uploaded_file.getvalue(), "text/plain"))
        ]
        try:
            response = requests.post(f"{API_URL}/apis/calls/upload_call", files=files)
            if response.status_code == 200:
                data = response.json()
                st.success("Upload successful!")
            else:
                st.error(f"Upload failed with status code {response.status_code}")
        except Exception as e:
            st.error(f"Error uploading file: {e}")

# uploaded_files = st.file_uploader("Select one or more transcript files (TXT)", type=["txt"],
#                                   accept_multiple_files=True)
#
# if st.button("Upload Call"):
#     if not uploaded_files:
#         st.warning("No files selected. Please upload at least one file.")
#     else:
#         # Prepare files for upload
#         files = []
#         for file in uploaded_files:
#             files.append(
#                 ("files", (file.name, file.getvalue(), "text/plain"))
#             )
#         try:
#             response = requests.post(f"{API_URL}/apis/calls/upload_call", files=files)
#             if response.status_code == 200:
#                 data = response.json()
#                 st.success(f"Upload successful!")
#             else:
#                 st.error(f"Upload failed with status code {response.status_code}")
#         except Exception as e:
#             st.error(f"Error uploading files: {e}")

st.markdown("## Call Summaries")

if st.button("Retrieve Summaries"):
    try:
        response = requests.get(f"{API_URL}/apis/calls/summaries")
        if response.status_code == 200:
            data = response.json()
            summaries = data.get("summaries", [])
            if not summaries:
                st.info("No summaries available.")
            else:
                for call in summaries:
                    st.markdown(f"**Call ID:** {call.get('call_id', 'N/A')}")
                    st.markdown(f"**Status:** {call.get('call_status', 'N/A')}")
                    st.markdown(f"**Raw Summary:** {call.get('raw_summary', 'N/A')}")
                    st.markdown(f"**Processed Summary:** {call.get('processed_summary', 'N/A')}")
                    if call.get("transcripts"):
                        st.markdown("**Transcripts:**")
                        for transcript in call["transcripts"]:
                            file_name = transcript.get('file_name', 'N/A')
                            file_content = transcript.get('file_content', '')
                            b64_file_content = base64.b64encode(file_content.encode()).decode()
                            href = f'<a href="data:text/plain;base64,{b64_file_content}" download="{file_name}">{file_name}</a>'

                            insight = transcript.get('insight', {})

                            st.markdown(f"- **File:** {href}", unsafe_allow_html=True)
                            st.markdown("  - **Insights:**")

                            insight_table = f"""
                            <table>
                                <tr><th>Payment Status</th><td>{insight.get('payment_status', 'N/A')}</td></tr>
                                <tr><th>Payment Amount</th><td>{insight.get('payment_amount', 'N/A')}</td></tr>
                                <tr><th>Payment Date</th><td>{insight.get('payment_date', 'N/A')}</td></tr>
                                <tr><th>Payment Method</th><td>{insight.get('payment_method', 'N/A')}</td></tr>
                                <tr><th>Summary Text</th><td>{insight.get('summary_text', 'N/A')}</td></tr>
                                <tr><th>User Modified Summary</th><td>{insight.get('user_modified_summary', 'N/A')}</td></tr>
                                <tr><th>LLM Retry Count</th><td>{insight.get('llm_retry_count', 'N/A')}</td></tr>
                                <tr><th>LLM Redo Required</th><td>{insight.get('llm_redo_required', 'N/A')}</td></tr>
                            </table>
                            """

                            st.markdown(insight_table, unsafe_allow_html=True)

                    st.markdown("---")
        else:
            st.error(f"Failed to fetch summaries: {response.status_code}")
    except Exception as e:
        st.error(f"Error fetching summaries: {e}")

# Define the backend health check URL
HEALTH_CHECK_URL = BACKEND_URL + "/health"

# Add a button to perform the health check
if st.button("Check Backend Health"):
    try:
        response = requests.get(HEALTH_CHECK_URL)
        if response.status_code == 200:
            health_status = response.json()
            st.success(f"Backend is healthy! Environment: {health_status['environment']}")
        else:
            st.error(f"Backend health check failed with status code: {response.status_code}")
    except Exception as e:
        st.error(f"Error performing health check: {str(e)}")
