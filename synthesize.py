import asyncio
import os
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import List
import edge_tts
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# --- Configuration ---
MAX_CHARS = 2000

def get_ffmpeg_path() -> str:
    """
    Locates ffmpeg executable.
    Checks imageio-ffmpeg first, then system PATH, then common Windows locations.
    Raises FileNotFoundError if not found.
    """
    # Try imageio-ffmpeg first
    try:
        import imageio_ffmpeg
        ffmpeg_cmd = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_cmd and os.path.exists(ffmpeg_cmd):
            return ffmpeg_cmd
    except ImportError:
        pass

    # Check PATH
    ffmpeg_cmd = shutil.which("ffmpeg")
    if ffmpeg_cmd:
        return ffmpeg_cmd
    
    # Check specific Windows paths
    common_paths = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        os.path.expanduser(r"~\ffmpeg\bin\ffmpeg.exe")
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
            
    raise FileNotFoundError(
        "FFmpeg not found! Please install FFmpeg and add it to your PATH, "
        "or place it in C:\\ffmpeg\\bin\\"
    )

def split_text_smart(text: str, max_chars: int = MAX_CHARS) -> List[str]:
    """
    Splits text into chunks respecting sentence boundaries where possible.
    """
    if len(text) <= max_chars:
        return [text]
        
    chunks = []
    current_chunk = ""
    
    sentences = text.replace('!', '!|').replace('?', '?|').replace('.', '.|').split('|')
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chars:
            current_chunk += sentence
        else:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            
            if len(sentence) > max_chars:
                for i in range(0, len(sentence), max_chars):
                    chunks.append(sentence[i:i+max_chars])
            else:
                current_chunk = sentence
                
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

async def _synthesize_chunk(text_chunk: str, output_path: str, voice: str) -> None:
    """Synthesizes a single chunk of text to file."""
    if not text_chunk.strip():
        return
    communicate = edge_tts.Communicate(text_chunk, voice)
    await communicate.save(output_path)

def synthesize_text_to_mp3(text: str, voice: str = "en-US-AriaNeural", progress_callback=None) -> str:
    """
    Synthesizes long text to a single MP3 file using edge-tts and ffmpeg concatenation.
    Returns path to final mp3.
    """
    ffmpeg_exe = get_ffmpeg_path()
    
    tmp_dir = tempfile.mkdtemp()
    chunks = split_text_smart(text)
    chunk_files = []
    
    total_chunks = len(chunks)
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    for idx, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
            
        chunk_file = Path(tmp_dir) / f"chunk_{idx}.mp3"
        
        loop.run_until_complete(_synthesize_chunk(chunk, str(chunk_file), voice))
        
        if chunk_file.exists():
            chunk_files.append(str(chunk_file))
            
        if progress_callback:
            progress_callback((idx + 1) / total_chunks)

    if not chunk_files:
        raise ValueError("No audio chunks generated! Text might be empty or invalid.")

    # Concatenate using ffmpeg concat demuxer
    # Create a list file for ffmpeg
    list_file_path = Path(tmp_dir) / "mylist.txt"
    with open(list_file_path, "w", encoding="utf-8") as f:
        for chunk_file in chunk_files:
            # ffmpeg requires forward slashes and safe paths
            safe_path = chunk_file.replace("\\", "/")
            f.write(f"file '{safe_path}'\n")

    final_mp3 = Path(tmp_dir) / "final_output.mp3"
    
    # Run ffmpeg command
    # ffmpeg -f concat -safe 0 -i mylist.txt -c copy output.mp3
    cmd = [
        ffmpeg_exe,
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file_path),
        "-c", "copy",
        "-y",  # Overwrite if exists
        str(final_mp3)
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg concatenation failed: {e.stderr.decode()}")

    return str(final_mp3)
