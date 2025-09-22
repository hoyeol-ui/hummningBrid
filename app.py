# app.py (프로젝트 루트 권장)
import streamlit as st
from pathlib import Path
from src.record import record_humming
from src.generate import generate_music, generate_music_midi

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
GEN_DIR = DATA_DIR / "generated"

st.set_page_config(page_title="Humming → Music", page_icon="🎶", layout="centered")
st.title("🎶 Humming → Music Prototype")

# 세션 상태
if "file_path" not in st.session_state:
    st.session_state["file_path"] = None
if "last_output" not in st.session_state:
    st.session_state["last_output"] = None

st.header("Step 1. 허밍 입력")
mode = st.radio("입력 방법", ["마이크로 녹음", "파일 업로드"], horizontal=True)

col1, col2 = st.columns(2)
with col1:
    if mode == "마이크로 녹음":
        if st.button("🎤 허밍 녹음 시작 (5초)"):
            path = record_humming(duration=5)
            st.session_state["file_path"] = path
            st.success(f"녹음 완료: {path}")
            st.audio(path)
    else:
        up = st.file_uploader("허밍 wav 업로드", type=["wav"])
        if up is not None:
            RAW_DIR.mkdir(parents=True, exist_ok=True)
            dest = RAW_DIR / up.name
            with open(dest, "wb") as f:
                f.write(up.getbuffer())
            st.session_state["file_path"] = str(dest)
            st.success(f"업로드 완료: {dest}")
            st.audio(str(dest))

with col2:
    st.write("")
    st.write("")
    if st.session_state["file_path"]:
        st.info(f"현재 허밍 파일: {st.session_state['file_path']}")

st.divider()
st.header("Step 2. 음악 생성 (Melody Conditioning)")

prompt = st.text_input("스타일 프롬프트(빈칸도 가능)", "gentle pop, calm, piano and light drums")
dur = st.slider("길이(초)", 5, 30, 15, 1)

if st.button("🚀 생성 시작"):
    f = st.session_state.get("file_path")
    if not f:
        st.error("허밍 파일이 필요합니다!")
    else:
        with st.spinner("생성 중… (첫 실행은 모델 다운로드로 시간이 좀 걸려요)"):
            out = generate_music_midi(f, out_name="melody_generated.wav", prompt=prompt, duration_sec=dur)
        st.session_state["last_output"] = out
        st.success("완료!")
        st.audio(out)

if st.session_state["last_output"]:
    st.download_button("⬇️ WAV 다운로드", data=open(st.session_state["last_output"], "rb").read(),
                       file_name="melody_generated.wav", mime="audio/wav")