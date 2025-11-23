import streamlit as st
from pathlib import Path
import os

# Try to import dependencies with error handling
try:
    import nest_asyncio
    from synthesize import synthesize_text_to_mp3, get_ffmpeg_path
except ImportError as e:
    st.error(f"❌ Dependency Error: {e}")
    st.warning("Please ensure all requirements are installed and 'requirements.txt' is pushed to GitHub.")
    st.stop()

st.set_page_config(page_title="Text to Speech Generator", layout="wide", page_icon="🗣️")

st.title("🗣️ Text to Speech Generator (Windows Friendly)")
st.markdown("""
Convert long text into natural-sounding speech using Microsoft Edge's Neural Voices.
**Features:** Unlimited length (auto-chunking), MP3 download, Windows optimized.
""")

# Sidebar for configuration
with st.sidebar:
    st.header("Settings")
    
    # Voice selection
    voice_options = {
        "English (US) - Aria (Female)": "en-US-AriaNeural",
        "English (US) - Guy (Male)": "en-US-GuyNeural",
        "English (US) - Jenny (Female)": "en-US-JennyNeural",
        "English (UK) - Libby (Female)": "en-GB-LibbyNeural",
        "English (UK) - Ryan (Male)": "en-GB-RyanNeural",
        "English (Australia) - Natasha (Female)": "en-AU-NatashaNeural",
        "English (Australia) - William (Male)": "en-AU-WilliamNeural",
    }
    
    selected_voice_name = st.selectbox(
        "Select Voice",
        options=list(voice_options.keys())
    )
    voice_code = voice_options[selected_voice_name]
    
    st.info("💡 Tip: Longer texts are automatically split into chunks to ensure high quality.")

    # Check FFmpeg status
    try:
        ffmpeg_path = get_ffmpeg_path()
        st.success(f"✅ FFmpeg detected")
    except FileNotFoundError:
        st.error("❌ FFmpeg not found!")
        st.warning("Please install FFmpeg to use this app.")

# Main area
text = st.text_area("Enter your text here:", height=300, placeholder="Paste your article, book chapter, or script here...")

col1, col2 = st.columns([1, 4])

with col1:
    generate_btn = st.button("Generate MP3", type="primary", use_container_width=True)

if generate_btn:
    if not text.strip():
        st.warning("Please enter some text first!")
    else:
        try:
            # Progress bar
            progress_bar = st.progress(0, text="Starting generation...")
            
            def update_progress(p):
                progress_bar.progress(p, text=f"Generating speech... {int(p*100)}%")

            mp3_path = synthesize_text_to_mp3(text, voice_code, progress_callback=update_progress)
            
            progress_bar.progress(1.0, text="Done!")
            st.success("✅ Speech generated successfully!")

            # Audio player and download
            mp3_file = Path(mp3_path)
            audio_bytes = mp3_file.read_bytes()
            
            st.audio(audio_bytes, format="audio/mp3")
            
            st.download_button(
                label="Download MP3",
                data=audio_bytes,
                file_name="speech_output.mp3",
                mime="audio/mp3",
                type="primary"
            )
            
        except FileNotFoundError as e:
            st.error(f"Configuration Error: {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
