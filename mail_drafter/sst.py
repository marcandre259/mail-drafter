import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import queue
import sys
import os
from pydub import AudioSegment

# --- Configuration ---
TEMP_WAV_FILENAME = "data/temp_live_recording.wav"  # Temporary WAV file
OUTPUT_MP3_FILENAME = "data/live_recording.mp3"  # Output MP3 filename
SAMPLE_RATE = 16000  # Lower sample rate for speech (common: 8000, 16000)
CHANNELS = 1  # Mono recording
DTYPE = "float32"  # Data type for audio samples
BUFFER_SIZE = 1024  # Size of audio buffer per callback
RECORD_SECONDS = (
    10  # Duration to record (in seconds) - set to None for indefinite recording
)
MP3_BITRATE = "32k"  # Low bitrate for MP3 (e.g., "32k", "64k")

# --- Global Variables ---
q = queue.Queue()
recording = threading.Event()


# --- Callback function for the audio stream ---
def callback(indata, frames, time, status):
    """This is called (in a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())


# --- Function to start recording ---
def start_recording():
    recording.set()  # Start recording initially
    print(f"Recording started. Press Ctrl+C to stop.")
    try:
        # Make sure the queue is empty before starting
        while not q.empty():
            q.get()

        # Open a temporary WAV file for writing
        with sf.SoundFile(
            TEMP_WAV_FILENAME,
            mode="w",
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            subtype="FLOAT",
        ) as file:
            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype=DTYPE,
                blocksize=BUFFER_SIZE,
                callback=callback,
            ):
                # This loop runs in the main thread, writing data from the queue
                while recording.is_set():
                    try:
                        data = q.get(
                            timeout=1
                        )  # Get data from the queue with a timeout
                        file.write(data)
                    except queue.Empty:
                        # No data in the queue, continue waiting
                        pass
                    except KeyboardInterrupt:
                        print("\nRecording stopped by user.")
                        recording.clear()  # Signal to stop the recording loop

    except Exception as e:
        print(f"An error occurred during recording: {e}")
    finally:
        print(f"Recording finished. Temporary WAV saved to {TEMP_WAV_FILENAME}")
        # Now, convert the temporary WAV to MP3
        convert_wav_to_mp3(TEMP_WAV_FILENAME, OUTPUT_MP3_FILENAME, MP3_BITRATE)
        # Clean up the temporary WAV file
        if os.path.exists(TEMP_WAV_FILENAME):
            os.remove(TEMP_WAV_FILENAME)
            print(f"Temporary WAV file {TEMP_WAV_FILENAME} removed.")

        return True


# --- Function to convert WAV to MP3 ---
def convert_wav_to_mp3(wav_filename, mp3_filename, bitrate):
    print(f"Converting {wav_filename} to {mp3_filename} with bitrate {bitrate}...")
    try:
        audio = AudioSegment.from_wav(wav_filename)
        audio.export(mp3_filename, format="mp3", bitrate=bitrate)
        print(f"Conversion complete. MP3 saved to {mp3_filename}")
    except Exception as e:
        print(f"An error occurred during MP3 conversion: {e}")
        print("Please ensure FFmpeg is installed and accessible in your system's PATH.")


# --- Main execution ---
if __name__ == "__main__":
    start_recording()
