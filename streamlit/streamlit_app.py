import base64
import time

import requests
import streamlit as st

from sample_transcripts_listing import display_sample_transcripts

# Set the backend URL. You can also set this in a secrets.toml file.
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")
API_URL = BACKEND_URL + st.secrets.get("API_PREFIX", "/api/v1")

st.title("Gen-AI Call Insight Extractor")

# Note about sample files
st.info("📌 Sample transcript files are available for download in the sidebar under 'Sample Transcripts'")

# Create tabs for main functionality
tab1, tab2, tab3 = st.tabs(["Upload Transcript", "Call Summaries", "Backend Status"])

# Tab 1: Upload Transcript
with tab1:
    st.header("Upload Transcript File(s)")

    # File uploader that allows multiple files with a limit of 4
    uploaded_files = st.file_uploader("Select the transcript file(s) (max 4 TXT files)...",
                                      type=["txt"],
                                      accept_multiple_files=True)

    if st.button("Process Transcripts") and uploaded_files:
        if len(uploaded_files) > 4:
            st.warning("A maximum of 4 transcripts are permitted per call!")
        elif len(uploaded_files) == 0:
            st.warning("No file(s) selected. Please upload a file.")
        else:
            # Create a files list for the multipart request
            files_list = [("files", (file.name, file.getvalue(), "text/plain"))
                          for file in uploaded_files]

            with st.spinner('Uploading transcripts...'):
                try:
                    response = requests.post(
                        f"{API_URL}/apis/calls/upload_call",
                        files=files_list
                    )

                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"Successfully uploaded {len(uploaded_files)} transcript(s)!")
                        # st.json(result)
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Failed to process transcripts: {str(e)}")

# Tab 2: Call Summaries
import pandas as pd
import streamlit as st

# Tab 2: Call Summaries
with tab2:
    st.header("Call Summaries")

    # Button for manual refresh
    refresh_button = st.button("Refresh Summaries")


    # Function to fetch summaries
    def fetch_summaries():
        try:
            with st.spinner("Retrieving summaries..."):
                response = requests.get(f"{API_URL}/apis/calls/summaries")

            if response.status_code == 200:
                data = response.json()
                summaries_list = data.get("summaries", [])
                enumerated_summaries_list = [(i, summary) for i, summary in enumerate(summaries_list, 1)]
                enumerated_summaries_list.reverse()  # Reverse to show newest first with correct numbering
                return enumerated_summaries_list, None, "Summaries refreshed successfully!"
            else:
                return [], f"Failed to fetch summaries: {response.status_code}", f"Error: Failed to fetch summaries (Status {response.status_code})"
        except Exception as e:
            return [], f"Error fetching summaries: {e}", f"Error: {str(e)}"


    # Initialize session state
    if "summaries_loaded" not in st.session_state:
        st.session_state.summaries_loaded = False
        st.session_state.summaries = []
        st.session_state.selected_call_index = None
        st.session_state.current_page = 0

    # Auto-fetch summaries if not loaded or if refresh button is clicked
    if not st.session_state.summaries_loaded or refresh_button:
        summaries_list, error, toast_message = fetch_summaries()

        # Show toast notification when refresh button is clicked
        if refresh_button:
            if error:
                st.toast(toast_message, icon="❌")
            else:
                st.toast(toast_message, icon="✅")

        if error:
            st.error(error)
        else:
            st.session_state.summaries = summaries_list
            st.session_state.summaries_loaded = True

    # Pagination settings
    items_per_page = 5
    summaries = st.session_state.summaries

    if not summaries:
        st.info("No summaries available.")
    else:
        # Determine total pages
        total_pages = (len(summaries) + items_per_page - 1) // items_per_page

        # Get current page summaries
        start_idx = st.session_state.current_page * items_per_page
        end_idx = min(start_idx + items_per_page, len(summaries))
        current_page_summaries = summaries[start_idx:end_idx]

        # Create DataFrame for display
        data = []
        for index, call in current_page_summaries:
            summary_text = call.get('ai_summary', call.get('raw_summary', 'None'))
            if summary_text:
                if len(summary_text) > 100:
                    summary_text = summary_text[:100] + "..."
            else:
                summary_text = "Processing..."

            data.append({
                "Call ID": str(index),
                "Status": call.get('call_status', 'Pending'),
                "AI Summary": summary_text
            })

        df = pd.DataFrame(data)

        # Custom CSS for better styling
        st.markdown("""
        <style>
        .call-table {font-size: 14px;}
        .call-table td {padding: 8px 5px;}
        .call-table th {font-weight: 600; background-color: #f0f2f6;}
        .detail-header {padding: 10px 0; font-size: 18px; font-weight: 600;}
        .call-table button {padding: 2px 6px; font-size: 12px;}
        </style>
        """, unsafe_allow_html=True)

        # Create interactive table
        st.markdown('<div class="call-table">', unsafe_allow_html=True)
        for i, row in df.iterrows():
            real_idx = i + start_idx
            cols = st.columns([0.5, 1, 5, 1])
            with cols[0]:
                st.write(row["Call ID"])
            with cols[1]:
                st.write(row["Status"])
            with cols[2]:
                st.write(row["AI Summary"])
            with cols[3]:
                if st.button("Details", key=f"view_{real_idx}"):
                    st.session_state.selected_call_index = real_idx
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Pagination controls
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if st.session_state.current_page > 0:
                if st.button("← Previous"):
                    st.session_state.current_page -= 1
                    st.rerun()

        with col2:
            st.write(f"Page {st.session_state.current_page + 1} of {total_pages}")

        with col3:
            if st.session_state.current_page < total_pages - 1:
                if st.button("Next →"):
                    st.session_state.current_page += 1
                    st.rerun()

    # Divider between table and details
    st.divider()

    # Detailed Call Information section
    st.markdown('<p class="detail-header">Detailed Call Information</p>', unsafe_allow_html=True)

    # Check if a call is selected
    if st.session_state.selected_call_index is not None and 0 <= st.session_state.selected_call_index < len(summaries):
        call = summaries[st.session_state.selected_call_index][1]

        # Add a close button to deselect the call
        col1, col2 = st.columns([5, 1])

        with col1:
            st.subheader("AI Summary")

        with col2:
            if st.button("✕", key="close_details"):
                st.session_state.selected_call_index = None
                st.rerun()

        # Display call details
        cols = st.columns(1)
        with cols[0]:
            st.markdown(f"{call.get('ai_summary', 'None')}")

        # Display transcripts
        if call.get("transcripts"):
            st.markdown("### Transcripts")
            for j, transcript in enumerate(call["transcripts"]):
                st.markdown(f"#### Transcript {j + 1}")

                # File download
                file_name = transcript.get('file_name', 'None')
                file_content = transcript.get('file_content', '')
                b64_file_content = base64.b64encode(file_content.encode()).decode()
                href = f'<a href="data:text/plain;base64,{b64_file_content}" download="{file_name}">{file_name}</a>'
                st.markdown(f"**Download:** {href}", unsafe_allow_html=True)

                # Display insights
                insight = transcript.get('insight', {})
                if insight:
                    st.markdown("##### Insights")

                    # Display in table format
                    insight_data = {
                        "Payment Status": insight.get('payment_status', 'None'),
                        "Payment Amount": insight.get('payment_amount', 'None'),
                        "Payment Date": insight.get('payment_date', 'None'),
                        "Payment Method": insight.get('payment_method', 'None')
                    }
                    st.table(insight_data)

                    st.markdown(f"**AI Summary:** {insight.get('ai_summary', 'None')}")
                    st.markdown(f"**User Summary:** {insight.get('user_summary', 'None')}")
                    st.markdown(f"**Refined Summary:** {insight.get('refined_summary', 'None')}")

                    # Add user summary form and refinement request button
                    with st.expander("Transcript Actions", expanded=False):
                        # User Summary Section
                        st.markdown("**User Summary**")
                        current_user_summary = insight.get('user_summary', '')
                        transcript_id = transcript.get('transcript_id', '')

                        # Create a unique key for this form
                        form_key = f"user_summary_form_{transcript_id}"

                        with st.form(key=form_key):
                            new_user_summary = st.text_area(
                                "Edit User Summary",
                                value=current_user_summary,
                                height=100,
                                key=f"summary_textarea_{transcript_id}"
                            )
                            submit_button = st.form_submit_button("Save User Summary")

                            if submit_button:
                                try:
                                    # Call API to update user summary
                                    update_url = f"{API_URL}/apis/transcripts/update_user_summary/{transcript_id}"
                                    response = requests.put(
                                        update_url,
                                        json={"user_summary": new_user_summary}
                                    )

                                    if response.status_code == 200:
                                        st.success("User summary updated successfully!")
                                        # Update local data
                                        insight['user_summary'] = new_user_summary
                                        # Refresh the page to show updated data
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to update: {response.text}")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")

                        # LLM Refinement Section
                        llm_refinement_required = insight.get('llm_refinement_required', False)
                        if llm_refinement_required:
                            st.markdown("**LLM Refinement**")
                            st.info("This transcript needs refinement")

                            if st.button("Request Refined Summary", key=f"refine_{transcript_id}"):
                                try:
                                    # Call API to request refinement
                                    refine_url = f"{API_URL}/apis/transcripts/generate_refined_summary/{transcript_id}"
                                    with st.spinner("Requesting refined summary..."):
                                        response = requests.post(refine_url)

                                    if response.status_code == 200:
                                        st.success("Summary refinement requested successfully!")
                                        # Refresh the page to show updated data
                                        time.sleep(1)  # Small delay to ensure backend processing
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to request refinement: {response.text}")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                else:
                    st.info("Insights are being processed... (30-60 seconds)")
    else:
        # Display a message when no call is selected
        st.info("Please select a call from the table above to view detailed information.")

# Tab 3: Backend Status
with tab3:
    st.header("Backend Status")

    # Define the backend health check URL
    HEALTH_CHECK_URL = BACKEND_URL + "/health"

    if st.button("Check Backend Health"):
        try:
            with st.spinner("Checking backend status..."):
                response = requests.get(HEALTH_CHECK_URL)
            if response.status_code == 200:
                health_status = response.json()
                st.success(f"Backend is healthy! Environment: {health_status['environment']}")

                # Display additional health metrics if available
                if health_status.get("details"):
                    st.json(health_status["details"])
            else:
                st.error(f"Backend health check failed with status code: {response.status_code}")
        except Exception as e:
            st.error(f"Error performing health check: {str(e)}")

# Sidebar for additional options
with st.sidebar.expander("Sample Transcripts"):
    display_sample_transcripts()
