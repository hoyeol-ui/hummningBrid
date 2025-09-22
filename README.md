
# HummingBrid 🎵

HummingBrid is a prototype application that turns simple humming into generated music.  
The goal of the project is to let anyone create short music pieces (≤ 3 minutes) from their own humming without requiring advanced musical knowledge.

---

## 🚀 Overview
- **Input**: User records a short humming sound (e.g., 5–10 seconds).
- **Processing**:
  1. Humming is recorded and preprocessed (mono, resampled).
  2. The melody is used as a conditioning signal for music generation.
  3. MusicGen (by Meta) generates a short music piece guided by the user’s humming and text prompts.
  4. (Future plan) Convert humming → MIDI → arrange accompaniment more naturally.
- **Output**: A `.wav` file containing music shaped by the user’s humming.

---

## 🛠 Features
- 🎤 **Real-time recording**: Record humming directly in the browser via Streamlit.
- 🎶 **Melody conditioning**: Uses [MusicGen](https://github.com/facebookresearch/audiocraft) for melody-guided generation.
- 🧩 **Modular pipeline**:
  - `record.py`: handles recording and saving raw humming.
  - `generate.py`: generates music conditioned on humming and text prompts.
  - `mix.py`: (planned) post-processing and mixing.
  - `stitch.py`: (planned) join multiple clips smoothly.
- 📦 **Web app interface**: Simple UI built with Streamlit for easy demo and testing.
- 💡 **Prototype for future extension**: The current version is slow (CPU fallback) and produces “abstract” results, but the pipeline is ready for refinement.

---

## 📂 Project Structure

hummingBrid/
│
├── app.py              # Main Streamlit app
├── requirements.txt    # Dependencies
├── src/
│   ├── generate.py     # Humming → Music generation
│   ├── record.py       # Recording module
│   ├── mix.py          # Mixing utilities (WIP)
│   └── stitch.py       # Stitching utilities (WIP)
└── data/
├── raw/            # Recorded humming
└── generated/      # Generated outputs

---

## ⚙️ Installation
```bash
git clone https://github.com/hoyeol-ui/hummingBrid.git
cd hummingBrid
python -m venv .venv
source .venv/bin/activate   # (or .venv\Scripts\activate on Windows)
pip install -r requirements.txt


⸻

▶️ Usage

Run the app:

streamlit run app.py

Steps:
	1.	Record your humming (about 5s).
	2.	Enter a text prompt (e.g., gentle pop with piano and light drums).
	3.	Wait for the model to generate the music.
	4.	Play back or download the generated result.

⸻

⚠️ Known Limitations
	•	Slow inference: On Mac M2, some operations fallback from MPS to CPU, making generation slower.
	•	Model size: Uses facebook/musicgen-melody (~1.2GB), which is heavy for real-time usage.
	•	Output quality: Current results sound abstract or noisy compared to expectations.
	•	Future direction: Explore humming → MIDI conversion and lightweight models for faster generation.

⸻

📌 Roadmap
	•	Improve stability of recording and preprocessing.
	•	Support humming → MIDI → accompaniment pipeline.
	•	Optimize for Apple Silicon (MPS backend).
	•	Add mixing/post-processing modules.
	•	Package as a distributable app.

⸻

📜 License

This project is for research and prototyping purposes only.
It builds upon Audiocraft (MusicGen) by Meta, under its license terms.

---
