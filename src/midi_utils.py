# src/midi_utils.py
from __future__ import annotations
from pathlib import Path
from typing import Optional

from basic_pitch.inference import predict_and_save

def _resolve_basic_pitch_model() -> str:
    """
    여러 basic-pitch 버전을 호환하기 위해
    모델 경로 상수를 다양한 이름으로 시도해서 찾아낸다.
    마지막으로는 패키지 내의 onnx 파일을 휴리스틱으로 탐색.
    """
    # 1) 가장 흔한 상수들 시도
    candidates = []
    try:
        from basic_pitch.constants import ICASSP_2022_MODEL_PATH  # 일부 버전
        candidates.append(ICASSP_2022_MODEL_PATH)
    except Exception:
        pass
    try:
        from basic_pitch.constants import DEFAULT_ONNX_MODEL_PATH  # 다른 버전
        candidates.append(DEFAULT_ONNX_MODEL_PATH)
    except Exception:
        pass

    for c in candidates:
        if c and Path(c).exists():
            return str(c)

    # 2) 패키지 내부를 직접 찾아보기 (버전에 따라 경로가 다를 수 있음)
    try:
        import basic_pitch, os
        pkg_dir = Path(basic_pitch.__file__).parent
        possible_rel = [
            "saved_models/icassp_2022/nmp.onnx",  # ✅ 실제 경로 반영
            "models/icassp_2022/model.onnx",
            "models/ICASS2022/model.onnx",
            "assets/icassp_2022/model.onnx",
            "assets/ICASS2022/model.onnx",
        ]
        for rel in possible_rel:
            p = pkg_dir / rel
            if p.exists():
                return str(p)
    except Exception:
        pass

    raise RuntimeError(
        "[basic-pitch] Could not locate the bundled ONNX model.\n"
        "-> Ensure onnxruntime is installed and your basic-pitch version bundles the ICASSP 2022 model.\n"
        "Try: pip install -U 'basic-pitch[onnx]' onnxruntime"
    )

def wav_to_midi(wav_path: str | Path, midi_path: str | Path) -> str:
    wav_path = Path(wav_path)
    midi_path = Path(midi_path)
    midi_path.parent.mkdir(parents=True, exist_ok=True)

    model_path = _resolve_basic_pitch_model()

    # basic-pitch는 파일을 폴더에 저장하는 방식이므로
    # 출력 폴더를 지정하면 같은 이름의 .mid가 생성됩니다.
    predict_and_save(
        [str(wav_path)],
        output_directory=str(midi_path.parent),
        save_midi=True,
        sonify_midi=False,
        save_model_outputs=False,
        save_notes=False,
        model_or_model_path=model_path,  # ★ 필수!
    )

    # 생성된 .mid 파일명이 입력 wav 기준으로 생성되므로, 우리가 원하는 이름으로 바꿔주기
    # (예: humming_20250922_170708_basic_pitch.mid -> 지정한 midi_path 이름으로 변경)
    # 폴더 내 .mid 하나만 있다고 가정하고 가장 최근 파일을 골라 rename
    mids = sorted(midi_path.parent.glob("*.mid"), key=lambda p: p.stat().st_mtime, reverse=True)
    if mids:
        mids[0].rename(midi_path)
    return str(midi_path)

def midi_to_wav(midi_path: str | Path, out_wav: str,
                sf2_path: str = "/Users/hy/soundfonts/FluidR3_GM.sf2",
                sr: int = 32000):
    import pretty_midi
    import soundfile as sf
    import numpy as np

    pm = pretty_midi.PrettyMIDI(str(midi_path))
    audio = pm.fluidsynth(fs=sr, sf2_path=sf2_path)

    # ✅ fallback: 오디오가 비거나 None이면 dummy sine wave 생성
    if audio is None or len(audio) == 0:
        print(f"[WARN] Empty audio from {midi_path}, using fallback sine wave.")
        t = np.linspace(0, 1, sr)
        audio = 0.1 * np.sin(2 * np.pi * 440 * t)  # 1초 A4 sine wave

    sf.write(out_wav, audio, sr)
    return out_wav

def midi_to_pianoroll(midi_path: str, fs: int = 100):
    import pretty_midi
    import numpy as np
    from pathlib import Path

    midi_path = Path(midi_path)  # 혹시 str로 들어와도 안전하게 Path화
    # ✅ pretty_midi는 str 경로 또는 파일 객체를 원함
    pm = pretty_midi.PrettyMIDI(str(midi_path))

    end_time = pm.get_end_time()
    n_frames = int(end_time * fs) + 1
    roll = np.zeros((128, n_frames), dtype=np.float32)

    for inst in pm.instruments:
        for note in inst.notes:
            start = int(note.start * fs)
            end = int(note.end * fs)
            roll[note.pitch, start:end] = note.velocity / 127.0

    return roll