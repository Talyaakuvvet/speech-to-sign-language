import re, csv, subprocess, tempfile
from pathlib import Path
import streamlit as st
# import whisper
# from st_audiorec import st_audiorec

# --- CONFIG ---
LEXICON_FILE = Path("lexicon.csv")
FS_DIR = Path("demo")   # hem kelime hem harf videoları burada
OUT_FILE = "asl_output.mp4"

# --- Load lexicon ---
def load_lexicon():
    lex = {}
    with open(LEXICON_FILE, newline='', encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) < 2:   # boş satırları atla
                continue
            word, path = row
            lex[word.strip().upper()] = path.strip()
    return lex


LEXICON = load_lexicon()

# --- Text normalize ---
STOPWORDS = {"the","a","an","is","are","am","to","at","of","on","in","and"}

def normalize_text(text: str) -> list[str]:
    text = re.sub(r"[^a-zA-Z0-9\s']", " ", text)
    tokens = [w for w in text.split() if w]
    base = []
    for w in tokens:
        lw = w.lower()
        if lw.endswith("ing") and len(lw) > 4: lw = lw[:-3]
        elif lw.endswith("ed") and len(lw) > 3: lw = lw[:-2]
        elif lw.endswith("es") and len(lw) > 3: lw = lw[:-2]
        elif lw.endswith("s") and len(lw) > 3: lw = lw[:-1]
        if lw not in STOPWORDS:
            base.append(lw)
    return base

def detect_fingerspelling(raw_text: str, tokens_norm: list[str]) -> set[int]:
    fs_idx = set()
    raw_words = re.findall(r"[A-Za-z]+", raw_text)
    norm_words = normalize_text(raw_text)

    # "my name is X" kalıbı
    for i in range(len(raw_words)-3):
        if raw_words[i].lower() == "my" and raw_words[i+1].lower() == "name" and raw_words[i+2].lower() == "is":
            candidate = raw_words[i+3]
            if candidate:
                norm_candidate = normalize_text(candidate)[0]
                for j, t in enumerate(tokens_norm):
                    if t == norm_candidate:
                        fs_idx.add(j)

    # Büyük harfle başlayan OOV kelimeler
    for j, nw in enumerate(norm_words):
        if nw.upper() not in LEXICON:
            if j < len(raw_words) and re.match(r"^[A-Z][a-z]+$", raw_words[j]):
                fs_idx.add(j)
    return fs_idx

def text_to_tokens(text: str):
    norm = normalize_text(text)
    fs_indices = detect_fingerspelling(text, norm)
    tokens = []
    for i, w in enumerate(norm):
        if i in fs_indices:
            tokens.append(("FS", list(w.upper())))
        else:
            if w.upper() in LEXICON:
                tokens.append(("WORD", w.upper()))
    return tokens

def tokens_to_clips(tokens):
    clips = []
    for tag, val in tokens:
        if tag == "WORD":
            clips.append(LEXICON[val])  # demo/ içindeki video
        elif tag == "FS":
            for letter in val:
                p = FS_DIR / f"{letter}.mp4"
                if p.exists():
                    clips.append(str(p))
    return clips

def concat_videos(paths, out_path=OUT_FILE):
    if not paths:
        return None
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        for p in paths:
            abs_path = str(Path(p).absolute())
            f.write(f"file '{abs_path}'\n")
        list_file = f.name
    cmd = [
        "ffmpeg","-y","-f","concat","-safe","0","-i",list_file,
        "-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac",out_path
    ]
    subprocess.run(cmd, check=False)
    return out_path

# --- Streamlit UI ---
st.set_page_config(page_title="Speech → Sign Language", layout="centered")
st.title("Speech → ASL Translation (Demo)")

text = st.text_input("Type an English sentence:", "Hello, my name is Talya")

if text and st.button("Translate to ASL"):
    tokens = text_to_tokens(text)
    clips = tokens_to_clips(tokens)
    if not clips:
        st.warning("No matching videos found.")
    else:
        out = concat_videos(clips)
        if out and Path(out).exists():
            st.video(str(Path(out).absolute()))
