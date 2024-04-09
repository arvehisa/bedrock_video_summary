import streamlit as st

time_part_summaries = [
    ("[10 min 30 sec] This is the summary for the first part of the meeting."),
    ("[25 min 15 sec] Discussion about project timeline and milestones."),
    ("[40 min 0 sec] Introduction and ice-breaker session.")
]

# Function to format time part summary with CSS
def format_time_part_summary(summary):
    time_part = summary[0:summary.index("]") + 1]  # Extract the time part inside square brackets
    summary_text = summary[summary.index("]") + 2:]  # Get the summary text outside square brackets

    summary_html = f"""
    <style>
    .time-part {{
        font-weight: bold;
        color: #FF4B4B;
    }}
    </style>
    <div>
    <span class="time-part">{time_part}</span> {summary_text}
    </div>
    """
    return st.markdown(summary_html, unsafe_allow_html=True)

# Function to process and transcribe the meeting recording
def process_recording(recording, video_url, description):
    # Placeholder function, replace with actual processing logic
    transcription = "Sample transcription text"
    summary = "Sample summary text"
    return transcription, summary

# Sidebar - left side of the screen
st.sidebar.title("Videosum")

# Input section
recording = st.sidebar.file_uploader("Upload meeting recording", type=["mp3", "wav", "flac"])
video_url = st.sidebar.text_input("Video URL (optional)")
description = st.sidebar.text_input("Description (optional)")

# Process button
if st.sidebar.button("Process Recording"):
    # Check if recording is uploaded
    if recording is None:
        st.sidebar.error("Please upload a meeting recording.")
    else:
        # Process the recording and get transcription and summary
        transcription, summary = process_recording(recording, video_url, description)

        # Main content - right side of the screen
        st.title("Meeting Summary")
        st.subheader("Transcription:")
        st.text(transcription)
        st.subheader("Summary:")
        st.text(summary)

        # Optional: Interact with a chatbot based on the transcript
        if st.button("Chat with Bot"):
            # Integrate with a chatbot API or logic here
            pass

# Uploaded videos list
uploaded_videos = ["Video 1", "Video 2", "Video 3"]

# Video summary section
selected_video = st.sidebar.selectbox("Select an uploaded video for summary", uploaded_videos)
if st.sidebar.button("Video Summary"):
    # Fetch and display the summary for the selected video
    st.title(f"Summary for {selected_video}")
    st.text("Summary text goes here.")

if st.sidebar.button("Time Part Summary"):
    for summary in time_part_summaries:
        format_time_part_summary(summary)

if st.sidebar.button("Transcription"):
    # Display time part summary for the selected video
    st.title(f"Transcription for {selected_video}")
    st.text("Transcriptions.")