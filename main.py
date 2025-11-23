import streamlit as st
from synthesize import synthesize_text_to_mp3, get_ffmpeg_path
from pathlib import Path
import os
import traceback

st.set_page_config(page_title="Text to Speech Generator", layout="wide", page_icon="🗣️")

st.title("🗣️ Text to Speech Generator (Windows Friendly)")
st.markdown("""
Convert long text into natural-sounding speech using Microsoft Edge's Neural Voices.

💡 **Features:**
- ✓ Unlimited text (auto chunking)
- ✓ High-quality Neural Voices
- ✓ MP3 download
- ✓ Windows & Cloud optimized
""")

# Sidebar configuration
with st.sidebar:
    st.header("Settings")
    
    voice_options = {
        "English (US) - Aria (Female)": "en-US-AriaNeural",
        "English (US) - Guy (Male)": "en-US-GuyNeural",
        "English (US) - Jenny (Female)": "en-US-JennyNeural",
        "English (UK) - Libby (Female)": "en-GB-LibbyNeural",
        "English (UK) - Ryan (Male)": "en-GB-RyanNeural",
        "English (Australia) - Natasha (Female)": "en-AU-NatashaNeural",
        "English (Australia) - William (Male)": "en-AU-WilliamNeural",
    }
    
    selected_voice_name = st.selectbox("Select Voice", list(voice_options.keys()))
    voice_code = voice_options[selected_voice_name]
    
    st.info("Long text is automatically divided into smaller chunks for better audio quality.")

    # FFmpeg validation
    try:
        ffmpeg_path = get_ffmpeg_path()
        st.success("✔ FFmpeg detected")
    except FileNotFoundError:
        st.error("❌ FFmpeg NOT detected!")
        st.warning("Install FFmpeg before generating voice.")
        st.stop()  # stop execution if ffmpeg missing

# Main text input
text = st.text_area("Enter your text here 👇", height=300, placeholder="Paste your text here...")

col1, col2 = st.columns([1, 4])

with col1:
    generate_btn = st.button("🎤 Generate MP3", use_container_width=True)

# Click handling
if generate_btn:
    if not text.strip():
        st.warning("⚠ Please enter some text first!")
        st.stop()
    
    try:
        # Progress indication
        progress_bar = st.progress(0, text="Starting voice generation...")

        def update_progress(p):
            progress_bar.progress(p, text=f"Generating speech... {int(p * 100)}%")

        # Call TTS synthesis
        mp3_path = synthesize_text_to_mp3(text, voice_code, progress_callback=update_progress)

        # Validate MP3 file
        if not mp3_path or not os.path.exists(mp3_path):
            st.error("❌ No audio file generated. Please check synthesize_text_to_mp3()")
            st.stop()

        audio_size = os.path.getsize(mp3_path)
        if audio_size == 0:
            st.error("❌ Generated MP3 is empty! Debug required in synthesize_text_to_mp3")
            st.stop()

        progress_bar.progress(1.0, text="✔ Done!")
        st.success(f"🎉 Audio generated successfully! File size: {audio_size} bytes")

        # Load audio
        mp3_file = Path(mp3_path)
        audio_bytes = mp3_file.read_bytes()

        st.audio(audio_bytes, format="audio/mp3")

        st.download_button(
            label="⬇ Download MP3",
            data=audio_bytes,
            file_name="speech_output.mp3",
            mime="audio/mp3"
        )

    except Exception as e:
        st.error(f"🚨 An error occurred: {e}")
        st.text(traceback.format_exc())
