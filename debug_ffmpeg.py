import os
import subprocess
import imageio_ffmpeg

def debug():
    print("Checking imageio-ffmpeg...")
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Path from imageio-ffmpeg: {exe}")
    
    if os.path.exists(exe):
        print("File exists.")
        try:
            # Try running it
            result = subprocess.run([exe, "-version"], capture_output=True, text=True)
            print("Version output (first line):")
            print(result.stdout.splitlines()[0])
        except Exception as e:
            print(f"Error running ffmpeg: {e}")
    else:
        print("File does not exist!")

if __name__ == "__main__":
    debug()
