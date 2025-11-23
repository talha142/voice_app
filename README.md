# TTS Generator

A Windows-compatible Text-to-Speech (TTS) application built with Streamlit, Edge-TTS, and Pydub.

## Features

- **Text-to-Speech**: Convert text to speech using Microsoft Edge's online TTS service.
- **Voice Selection**: Choose from a variety of voices and languages.
- **Audio Processing**: Merge multiple audio chunks (if implemented) and manage audio output.
- **Streamlit UI**: Simple and interactive web interface.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/yourusername/tts_project.git
    cd tts_project
    ```

2.  Create a virtual environment:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Install FFmpeg:
    - Ensure `ffmpeg` is installed and added to your system PATH.

## Usage

Run the Streamlit application:

```bash
streamlit run main.py
```

## Project Structure

- `main.py`: Main Streamlit application entry point.
- `synthesize.py`: Core TTS synthesis logic.
- `utils_audio.py`: Audio processing utilities.
- `audio_output/`: Directory for generated audio files.

## License

MIT
