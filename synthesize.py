import asyncio
import os
import tempfile
import shutil
import subprocess
import threading
from pathlib import Path
from typing import List
import edge_tts

# --- Configuration ---
MAX_CHARS = 2000  # Under 2500 to avoid TTS API issues


# ---------------------------------------------------------
# FFmpeg Detection
# ---------------------------------------------------------
def get_ffmpeg_path() -> str:
    """Finds a valid FFmpeg executable."""
    try:
        import imageio_ffmpeg
        ffmpeg_cmd = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_cmd and os.path.exists(ffmpeg_cmd):
            return ffmpeg_cmd
    except ImportError:
        pass

    ffmpeg_cmd = shutil.which("ffmpeg")
    if ffmpeg_cmd:
        return ffmpeg_cmd

    common_paths = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        os.path.expanduser(r"~\ffmpeg\bin\ffmpeg.exe"),
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path

    raise FileNotFoundError("FFmpeg not found. Please install and add to PATH.")


# ---------------------------------------------------------
# Smart Chunking
# ---------------------------------------------------------
def split_text_smart(text: str, max_chars: int = MAX_CHARS) -> List[str]:
    """Split text intelligently into sentence-based chunks."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    current_chunk = ""

    # Split sentences with markers
    sentences = text.replace("!", "!|").replace("?", "?|").replace(".", ".|").split("|")

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(current_chunk) + len(sentence) <= max_chars:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


# ---------------------------------------------------------
# Async TTS Generation (Safe With Retries)
# ---------------------------------------------------------
async def _synthesize_chunk_async(text_chunk: str, output_path: str, voice: str, retries=3):
    """Generate a chunk using Edge-TTS with retry and output validation."""
    if not text_chunk.strip():
        return

    for attempt in range(1, retries + 1):
        try:
            communicate = edge_tts.Communicate(text_chunk, voice)
            await communicate.save(output_path)

            # Validate audio file
            if os.path.exists(output_path) and os.path.getsize(output_path) > 500:
                return  # SUCCESS

            # If audio empty → retry
            if attempt < retries:
                continue

            raise RuntimeError("No audio was received for this chunk.")

        except Exception as e:
            if attempt == retries:
                raise RuntimeError(f"TTS chunk failed after retries: {e}")


# ---------------------------------------------------------
# Run Async Loop Safely
# ---------------------------------------------------------
def _run_async_synthesis(chunks: List[str], tmp_dir: str, voice: str, progress_callback=None) -> List[str]:
    """Creates an async loop and generates all chunks reliably."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    chunk_files = []
    total_chunks = len(chunks)

    try:
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue

            chunk_file = Path(tmp_dir) / f"TTS_chunk_{i}.mp3"

            loop.run_until_complete(
                _synthesize_chunk_async(chunk, str(chunk_file), voice)
            )

            # Final validation
            if not chunk_file.exists() or os.path.getsize(chunk_file) <= 500:
                raise RuntimeError(f"Chunk {i} produced EMPTY audio (after retry).")

            chunk_files.append(str(chunk_file))

            if progress_callback:
                progress_callback((i + 1) / total_chunks)

    finally:
        loop.close()

    return chunk_files


# ---------------------------------------------------------
# Main TTS Function
# ---------------------------------------------------------
def synthesize_text_to_mp3(text: str, voice: str = "en-US-AriaNeural", progress_callback=None) -> str:
    """Converts long text into high-quality MP3 using chunking + FFmpeg."""
    ffmpeg_exe = get_ffmpeg_path()

    if not text.strip():
        raise ValueError("Input text is empty!")

    # Create temp dir
    tmp_dir = tempfile.mkdtemp()
    chunks = split_text_smart(text)

    results = {"chunk_files": [], "error": None}

    # Run synthesis in a worker thread
    def synthesis_worker():
        try:
            results["chunk_files"] = _run_async_synthesis(
                chunks, tmp_dir, voice, progress_callback
            )
        except Exception as e:
            results["error"] = str(e)

    thread = threading.Thread(target=synthesis_worker)
    thread.start()
    thread.join()

    if results["error"]:
        raise RuntimeError(f"TTS synthesis failed: {results['error']}")

    chunk_files = results["chunk_files"]
    if not chunk_files:
        raise RuntimeError("No audio chunks were generated!")

    # Create FFmpeg concat filelist
    list_file = Path(tmp_dir) / "chunks.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for file in chunk_files:
            safe_path = file.replace("\\", "/")
            f.write(f"file '{safe_path}'\n")

    final_mp3 = Path(tmp_dir) / "speech_output.mp3"

    # FFmpeg concat
    try:
        subprocess.run(
            [
                ffmpeg_exe,
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_file),
                "-c", "copy",
                "-y",
                str(final_mp3)
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg failed: {e.stderr.decode()}")

    if not final_mp3.exists() or os.path.getsize(final_mp3) < 500:
        raise RuntimeError("Final MP3 not generated properly!")

    return str(final_mp3)
