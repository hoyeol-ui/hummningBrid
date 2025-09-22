from pydub import AudioSegment
import os

INPUT_DIR = "data/generated"
OUTPUT_DIR = "data/final"

def stitch_pieces(file_list, output_name="stitched_song.wav"):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    combined = AudioSegment.from_wav(file_list[0])
    for f in file_list[1:]:
        seg = AudioSegment.from_wav(f)
        combined = combined.append(seg, crossfade=2000)  # 2초 crossfade

    out_file = os.path.join(OUTPUT_DIR, output_name)
    combined.export(out_file, format="wav")
    print(f"✅ 이어붙인 곡 저장 완료: {out_file}")
    return out_file

if __name__ == "__main__":
    files = [os.path.join(INPUT_DIR, f) for f in sorted(os.listdir(INPUT_DIR))]
    stitch_pieces(files)