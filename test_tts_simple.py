from synthesize import synthesize_text_to_mp3
import os

print("Testing synthesize_text_to_mp3 function...")
text = "This is a test of the wrapper function."
voice = "en-US-AriaNeural"

try:
    mp3_path = synthesize_text_to_mp3(text, voice)
    print(f"✅ Success! Generated: {mp3_path}")
    if os.path.exists(mp3_path):
        print(f"   File size: {os.path.getsize(mp3_path)} bytes")
except Exception as e:
    print(f"❌ Failed: {e}")
