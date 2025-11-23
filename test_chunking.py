import unittest
from synthesize import split_text_smart

class TestChunking(unittest.TestCase):
    def test_short_text(self):
        text = "Hello world."
        chunks = split_text_smart(text, max_chars=100)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)

    def test_long_text_split(self):
        # Create text that is slightly longer than max_chars
        # "Hello world. " * 10 is 130 chars.
        text = "Hello world. " * 10
        chunks = split_text_smart(text, max_chars=50)
        
        self.assertTrue(len(chunks) > 1)
        # Verify no chunk exceeds limit
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 50)
            
        # Verify content is preserved
        self.assertEqual("".join(chunks), text)

    def test_sentence_boundary(self):
        s1 = "This is sentence one."
        s2 = "This is sentence two."
        text = f"{s1} {s2}"
        # max_chars just enough for one sentence
        chunks = split_text_smart(text, max_chars=len(s1) + 5)
        
        self.assertIn(s1, chunks[0])
        self.assertIn(s2, chunks[1] if len(chunks) > 1 else chunks[0])

if __name__ == "__main__":
    unittest.main()
