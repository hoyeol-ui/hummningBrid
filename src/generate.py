# src/generate.py
import os
from pathlib import Path

import torch
import torchaudio
from audiocraft.models import MusicGen

_DEVICE = "cpu"   # 원래 "cuda" or "mps"였던 부분을 cpu로 강제
_MODEL = None

def get_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = MusicGen.get_pretrained("facebook/musicgen-melody", device=_DEVICE)
    return _MODEL

DATA_DIR = Path("data")
GEN_DIR = DATA_DIR / "generated"
SAMPLE_RATE = 32000

def _device():
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"   # Whisper처럼 우선 MPS 시도
    return "cpu"

_DEVICE = _device()

def get_model():
    global _MODEL
    if _MODEL is None:
        try:
            _MODEL = MusicGen.get_pretrained("facebook/musicgen-melody", device=_DEVICE)
        except RuntimeError as e:
            print(f"[WARN] {_DEVICE}에서 실행 실패 → CPU로 fallback: {e}")
            _MODEL = MusicGen.get_pretrained("facebook/musicgen-melody", device="cpu")
    return _MODEL

def _load_wav_mono(path: str | Path, target_sr: int = SAMPLE_RATE) -> tuple[torch.Tensor, int]:
    wav, sr = torchaudio.load(str(path))
    if wav.shape[0] > 1:
        wav = torch.mean(wav, dim=0, keepdim=True)  # mono
    if sr != target_sr:
        wav = torchaudio.functional.resample(wav, sr, target_sr)
        sr = target_sr
    return wav, sr

def generate_music(
    humming_wav: str | Path,
    out_name: str = "generated.wav",
    prompt: str = "gentle pop, calm, piano and light drums",
    duration_sec: int = 15,
    top_k: int = 250,
    temperature: float = 1.0,
) -> str:
    """
    허밍 Wav를 melody conditioning으로 사용해 잔잔한 팝 음악 생성.
    반환: 생성된 wav 파일 경로
    """
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    model = get_model()

    # 생성 파라미터
    model.set_generation_params(
        duration=duration_sec,
        top_k=top_k,
        temperature=temperature,
        two_step_cfg=True,
    )

    # 허밍 로드 (멜로디 컨디셔닝)
    mel, sr = _load_wav_mono(humming_wav, SAMPLE_RATE)

    # 핵심: melody_wavs + melody_sample_rate
    pieces = model.generate_with_chroma(
        descriptions=[prompt],
        melody_wavs=[mel.cpu()],  # (1, T) 유지
        melody_sample_rate=sr,
        progress=True,
    )

    audio = pieces[0]  # torch.Tensor [T] @ 32k
    out_path = GEN_DIR / out_name
    # (1, T) 형태로 변환 (channels=1)
    if audio.dim() == 1:
        audio = audio.unsqueeze(0)
    torchaudio.save(str(out_path), audio.cpu(), SAMPLE_RATE)
    return str(out_path)