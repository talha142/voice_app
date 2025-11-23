import time
from synthesize import synthesize_text_to_mp3

def test_long_generation():
    print("Generating 5000-word text...")
    # Average word length is ~5 chars. 5000 words * 6 (char+space) = ~30,000 chars.
    # Let's be safe and generate ~30k chars.
    base_sentence = "This is a test sentence to verify the long text capabilities of the text to speech generator. "
    # base_sentence is ~90 chars. 30000 / 90 = ~333 repetitions.
    long_text = base_sentence * 350
    
    word_count = len(long_text.split())
    char_count = len(long_text)
    
    print(f"Text generated: {word_count} words, {char_count} characters.")
    
    print("Starting synthesis...")
    start_time = time.time()
    
    try:
        output_path = synthesize_text_to_mp3(long_text)
        duration = time.time() - start_time
        
        print(f"Success! Audio saved to: {output_path}")
        print(f"Time taken: {duration:.2f} seconds")
        
    except Exception as e:
        print(f"Generation failed: {e}")

if __name__ == "__main__":
    test_long_generation()
