import asyncio
import os
from synthesize import synthesize_text_to_mp3

def test_generation():
    print("Testing TTS generation...")
    text = "Hello! This is a test of the Edge TTS system. It should sound natural."
    try:
        output_path = synthesize_text_to_mp3(text)
        print(f"Success! Audio saved to: {output_path}")
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print("File exists and is not empty.")
        else:
            print("Error: File not found or empty.")
            
    except Exception as e:
        print(f"Generation failed: {e}")

if __name__ == "__main__":
    test_generation()
