import torchaudio
import matplotlib.pyplot as plt
from pathlib import Path

final_path = Path("data/final/mixed_song.wav")
out_dir = Path("data/analysis")
out_dir.mkdir(parents=True, exist_ok=True)

if final_path.exists():
    waveform, sr = torchaudio.load(final_path)

    # 파형 저장
    plt.figure(figsize=(12, 4))
    plt.plot(waveform.t().numpy())
    plt.title(f"Waveform of {final_path.name} (sr={sr})")
    plt.xlabel("Time (samples)")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.savefig(out_dir / "waveform.png")
    plt.close()

    # 스펙트로그램 저장
    spec = torchaudio.transforms.MelSpectrogram(sample_rate=sr)(waveform)
    spec_db = torchaudio.transforms.AmplitudeToDB()(spec)

    plt.figure(figsize=(12, 6))
    plt.imshow(spec_db[0].numpy(), aspect="auto", origin="lower")
    plt.title(f"Mel Spectrogram of {final_path.name}")
    plt.colorbar(label="dB")
    plt.xlabel("Time (frames)")
    plt.ylabel("Mel bins")
    plt.tight_layout()
    plt.savefig(out_dir / "spectrogram.png")
    plt.close()

    print("✅ 그래프 저장 완료:", out_dir)
else:
    print("❌ data/final/mixed_song.wav not found.")