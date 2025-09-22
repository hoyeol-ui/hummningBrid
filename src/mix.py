import soundfile as sf
from pedalboard import Pedalboard, Reverb, Compressor, Gain
import os

INPUT_FILE = "data/final/stitched_song.wav"
OUTPUT_FILE = "data/final/mixed_song.wav"

def apply_effects(input_file=INPUT_FILE, output_file=OUTPUT_FILE):
    audio, sr = sf.read(input_file)

    board = Pedalboard([
        Gain(gain_db=3),
        Compressor(threshold_db=-16, ratio=2.5),
        Reverb(room_size=0.5, wet_level=0.3)
    ])

    effected = board(audio, sr)
    sf.write(output_file, effected, sr)
    print(f"✅ 믹싱 완료: {output_file}")

if __name__ == "__main__":
    apply_effects()