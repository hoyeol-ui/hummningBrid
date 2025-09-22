# src/record.py
from datetime import datetime
from pathlib import Path
import sounddevice as sd
import soundfile as sf

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
SAMPLE_RATE = 32000  # AudioCraft 기본

def record_humming(duration=5, samplerate=SAMPLE_RATE) -> str:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    filename = RAW_DIR / f"humming_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    print(f"🎤 {duration}s 녹음 시작…")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()
    sf.write(str(filename), audio, samplerate)
    print(f"✅ 저장: {filename}")
    return str(filename)

if __name__ == "__main__":
    record_humming()