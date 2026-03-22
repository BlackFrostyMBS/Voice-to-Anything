"""
Voice to Anything - Dictation Tool
Transcribes your speech and types it into any active window.

Controls:
  F9  - Manual mode: press to start recording, press again to stop and type
  F8  - Auto mode: toggle always-on listening (detects speech automatically)
  ESC - Quit
"""

import sys
import os

# Add whisper-flow to path if installed locally
_whisperflow_path = os.path.join(os.path.dirname(__file__), "whisper-flow")
if os.path.exists(_whisperflow_path):
    sys.path.insert(0, _whisperflow_path)

# Add ffmpeg to PATH if installed via winget
_ffmpeg_path = os.path.expandvars(
    r"%LOCALAPPDATA%\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin"
)
if os.path.exists(_ffmpeg_path):
    os.environ["PATH"] = _ffmpeg_path + os.pathsep + os.environ["PATH"]

import threading
import tempfile
import wave
import time
import pyaudio
import whisper
import pyperclip
import keyboard
import pyautogui
import numpy as np

# --- Settings ---
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK = 1024
FORMAT = pyaudio.paInt16
MANUAL_KEY = "f9"
AUTO_KEY = "f8"
QUIT_KEY = "esc"

# Auto-mode VAD settings
SILENCE_THRESHOLD = 500    # audio energy below this = silence
SILENCE_SECONDS = 1.5      # seconds of silence before auto-transcribe
MIN_SPEECH_SECONDS = 0.5   # ignore blips shorter than this

# --- State ---
recording = False
auto_mode = False
frames = []
audio = pyaudio.PyAudio()

print("=" * 48)
print("        Voice to Anything - v1.0")
print("=" * 48)
print()
print("  Loading Whisper model...")
model = whisper.load_model("base")
print("  Model ready. Supports 99 languages.")
print()
print("  F9  - Manual: press to record, press again to type")
print("  F8  - Auto:   always-on, types when you pause")
print("  ESC - Quit")
print()
print("  Tip: click inside any window before speaking")
print("=" * 48)
print()


def get_energy(data):
    samples = np.frombuffer(data, dtype=np.int16)
    return np.abs(samples).mean()


def transcribe_and_type(audio_frames):
    if not audio_frames:
        return

    print("Transcribing...")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp_path = f.name

    wf = wave.open(tmp_path, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b"".join(audio_frames))
    wf.close()

    result = model.transcribe(tmp_path)
    os.unlink(tmp_path)

    text = result["text"].strip()
    if not text:
        print("Nothing detected.")
        return

    print(f'Typing: "{text}"')
    pyperclip.copy(text + " ")
    time.sleep(0.1)
    pyautogui.hotkey("ctrl", "v")


# --- Manual mode ---

def record_audio_manual():
    global frames
    frames = []
    stream = audio.open(
        format=FORMAT, channels=CHANNELS,
        rate=SAMPLE_RATE, input=True,
        frames_per_buffer=CHUNK,
    )
    print("Recording... (press F9 to stop and transcribe)")
    while recording:
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    stream.stop_stream()
    stream.close()


def toggle_manual(event):
    global recording
    if auto_mode:
        print("Turn off auto mode (F8) before using manual mode.")
        return
    if not recording:
        recording = True
        threading.Thread(target=record_audio_manual, daemon=True).start()
    else:
        recording = False
        time.sleep(0.2)
        transcribe_and_type(frames)


# --- Auto mode ---

def auto_listen_loop():
    stream = audio.open(
        format=FORMAT, channels=CHANNELS,
        rate=SAMPLE_RATE, input=True,
        frames_per_buffer=CHUNK,
    )
    print("Auto mode ON - listening... speak and it will type automatically")

    speech_frames = []
    silent_chunks = 0
    speaking = False
    chunks_per_second = SAMPLE_RATE / CHUNK
    silence_chunk_limit = int(SILENCE_SECONDS * chunks_per_second)
    min_speech_chunks = int(MIN_SPEECH_SECONDS * chunks_per_second)

    while auto_mode:
        data = stream.read(CHUNK, exception_on_overflow=False)
        energy = get_energy(data)

        if energy > SILENCE_THRESHOLD:
            speaking = True
            silent_chunks = 0
            speech_frames.append(data)
        else:
            if speaking:
                silent_chunks += 1
                speech_frames.append(data)
                if silent_chunks >= silence_chunk_limit:
                    if len(speech_frames) >= min_speech_chunks:
                        transcribe_and_type(speech_frames)
                    speech_frames = []
                    silent_chunks = 0
                    speaking = False

    stream.stop_stream()
    stream.close()
    print("Auto mode OFF.")


def toggle_auto(event):
    global auto_mode, recording
    if recording:
        print("Stop manual recording (F9) before switching to auto mode.")
        return
    auto_mode = not auto_mode
    if auto_mode:
        threading.Thread(target=auto_listen_loop, daemon=True).start()


# --- Quit ---

def quit_app(event):
    global recording, auto_mode
    recording = False
    auto_mode = False
    print("\nGoodbye!")
    os._exit(0)


keyboard.on_press_key(MANUAL_KEY, toggle_manual)
keyboard.on_press_key(AUTO_KEY, toggle_auto)
keyboard.on_press_key(QUIT_KEY, quit_app)

keyboard.wait()
