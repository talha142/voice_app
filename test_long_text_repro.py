from synthesize import synthesize_text_to_mp3
import os

def test_long_text():
    print("Testing synthesize_text_to_mp3 with LONG text...")
    # Generate a long text (approx 5000 chars)
    long_text = "This is a test sentence to simulate a long paragraph. " * 100
    long_text += "\n\n" + "Another paragraph with some special characters: !?., " * 50
    
    print(f"Text length: {len(long_text)} characters")
    
    try:
        output_path = synthesize_text_to_mp3(long_text)
        print(f"Success! Output saved to: {output_path}")
        if os.path.exists(output_path):
            print(f"Size: {os.path.getsize(output_path)} bytes")
    except Exception as e:
        print(f"CAUGHT ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_long_text()
