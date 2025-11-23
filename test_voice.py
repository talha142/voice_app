# test_voice.py
import os
from TTS.api import TTS

os.makedirs("audio_output", exist_ok=True)

def test_generate():
    # Choose a simple model that should download via TTS package
    model_name = "tts_models/en/vctk/vits"
    print("Loading model:", model_name)
    tts = TTS(model_name)
    text = "Hello. This is a quick test to verify the TTS installation. If you hear this, it works."
    out_path = "audio_output/test_voice.wav"
    print("Generating to:", out_path)
    tts.tts_to_file(text=text, file_path=out_path)
    print("Done. Check:", out_path)

if __name__ == "__main__":
    test_generate()
