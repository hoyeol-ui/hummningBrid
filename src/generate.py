# src/generate.py
import argparse
from pathlib import Path

import torch
import torchaudio
from audiocraft.models import MusicGen

# MIDI 유틸
from src.midi_utils import wav_to_midi, midi_to_wav

# ====== 기본 경로/상수 ======
DATA_DIR = Path("data")
GEN_DIR = DATA_DIR / "generated"
SAMPLE_RATE = 32000

# ====== 디바이스 선택 + 모델 로딩 ======
_MODEL = None


def _select_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def get_model():
    """MusicGen 모델을 (가능하면) 가속 디바이스로, 실패 시 CPU로 로드."""
    global _MODEL
    if _MODEL is None:
        device = _select_device()
        try:
            _MODEL = MusicGen.get_pretrained("facebook/musicgen-melody", device=device)
        except Exception as e:
            print(f"[WARN] {device}에서 실행 실패 → CPU로 fallback: {e}")
            _MODEL = MusicGen.get_pretrained("facebook/musicgen-melody", device="cpu")
    return _MODEL


# ====== 오디오 유틸 ======
def _load_wav_mono(path: str | Path, target_sr: int = SAMPLE_RATE) -> tuple[torch.Tensor, int]:
    """(channels, time) 형태 mono 로드 + 리샘플"""
    wav, sr = torchaudio.load(str(path))
    if wav.dim() == 1:
        wav = wav.unsqueeze(0)
    if wav.shape[0] > 1:
        wav = torch.mean(wav, dim=0, keepdim=True)  # mono
    if sr != target_sr:
        wav = torchaudio.functional.resample(wav, sr, target_sr)
        sr = target_sr
    return wav, sr


# ====== 생성 함수 (MIDI 경유) ======
def generate_music_midi(
    humming_wav: str | Path,
    out_name: str = "generated_midi.wav",
    prompt: str = "calm piano",
    duration_sec: int = 15,
) -> str:
    """
    1) 허밍 WAV → MIDI
    2) MIDI → WAV (melody conditioning 신호로 사용)
    3) MusicGen.generate_with_chroma 로 최종 생성
    """
    GEN_DIR.mkdir(parents=True, exist_ok=True)

    model = get_model()
    model.set_generation_params(duration=duration_sec, top_k=250, temperature=1.0)

    # 1) 허밍 → MIDI
    midi_dir = Path("data/midi")
    midi_dir.mkdir(parents=True, exist_ok=True)
    midi_path = midi_dir / (Path(out_name).stem + ".mid")
    wav_to_midi(humming_wav, midi_path)

    # 2) MIDI → WAV (melody conditioning)
    melody_wav_path = midi_to_wav(midi_path, out_wav=str(midi_dir / "melody_condition.wav"))

    # 3) melody conditioning 로드
    mel, sr = torchaudio.load(melody_wav_path)
    if mel.dim() == 1:
        mel = mel.unsqueeze(0)  # (1, T)

    # 4) 생성
    pieces = model.generate_with_chroma(
        descriptions=[prompt],
        melody_wavs=[mel],          # torch.Tensor (channels, time)
        melody_sample_rate=sr,
        progress=True,
    )

    audio = pieces[0]  # [T] 또는 [C, T]
    if audio.dim() == 1:
        audio = audio.unsqueeze(0)  # (1, T)

    out_path = GEN_DIR / out_name
    torchaudio.save(str(out_path), audio.cpu(), SAMPLE_RATE)
    return str(out_path)


# ====== 생성 함수 (직접 허밍 오디오 컨디셔닝) ======
def generate_music(
    humming_wav: str | Path,
    out_name: str = "generated.wav",
    prompt: str = "gentle pop, calm, piano and light drums",
    duration_sec: int = 15,
    top_k: int = 250,
    temperature: float = 1.0,
) -> str:
    """
    허밍 WAV 자체를 melody conditioning 으로 사용.
    """
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    model = get_model()

    model.set_generation_params(
        duration=duration_sec,
        top_k=top_k,
        temperature=temperature,
        two_step_cfg=True,
    )

    mel, sr = _load_wav_mono(humming_wav, SAMPLE_RATE)

    pieces = model.generate_with_chroma(
        descriptions=[prompt],
        melody_wavs=[mel.cpu()],  # (1, T)
        melody_sample_rate=sr,
        progress=True,
    )

    audio = pieces[0]
    if audio.dim() == 1:
        audio = audio.unsqueeze(0)

    out_path = GEN_DIR / out_name
    torchaudio.save(str(out_path), audio.cpu(), SAMPLE_RATE)
    return str(out_path)


# ====== CLI: MIDI -> WAV 유틸 ======
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MIDI to WAV (via FluidSynth) helper")
    parser.add_argument("--midi", type=str, required=True, help="Input MIDI file path")
    parser.add_argument("--out", type=str, required=True, help="Output WAV file path")
    args = parser.parse_args()

    out_path = midi_to_wav(args.midi, out_wav=args.out)
    print(f"✅ WAV 저장 완료: {out_path}")