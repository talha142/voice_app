# utils_audio.py
from pydub import AudioSegment
from typing import List

def concat_audio_files(input_paths: List[str], out_path: str, format: str = "mp3"):
    if not input_paths:
        raise ValueError("input_paths empty")
    combined = AudioSegment.from_file(input_paths[0])
    for p in input_paths[1:]:
        combined += AudioSegment.from_file(p)
    combined.export(out_path, format=format)
    return out_path
