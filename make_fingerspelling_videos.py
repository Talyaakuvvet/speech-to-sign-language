import os, glob, subprocess
from pathlib import Path

# 1) ŞU KÖK KLASÖRÜ KULLAN: fingerspelling/asl_alphabet_train
# (İçinde bir klasör daha olabilir; script kendisi bulacak.)
RAW_ROOT = Path("fingerspelling/asl_alphabet_train")
OUT = Path("clips/fingerspelling")
OUT.mkdir(parents=True, exist_ok=True)

LETTERS = [chr(c) for c in range(ord('A'), ord('Z')+1)]

def find_letter_folder(root: Path, letter: str) -> Path | None:
   
    # doğrudan var mı?
    d1 = root / letter
    if d1.is_dir():
        return d1
    # bir alt seviyede var mı?
    # örn: root/asl_alphabet_train/A veya root/train/A
    for p in root.iterdir():
        if p.is_dir():
            d2 = p / letter
            if d2.is_dir():
                return d2
    # daha derinlerde ara (yavaş ama tek seferlik)
    candidates = list(root.rglob(f"{letter}"))
    for c in candidates:
        if c.is_dir():
            return c
    return None

def pick_image(letter_dir: Path) -> str | None:
    """
    JPG/PNG dosyalarını rekürsif ara; en büyük boyutlu olanı seç (genelde daha net).
    """
    files = []
    files += list(letter_dir.rglob("*.jpg"))
    files += list(letter_dir.rglob("*.JPG"))
    files += list(letter_dir.rglob("*.jpeg"))
    files += list(letter_dir.rglob("*.png"))
    files += list(letter_dir.rglob("*.PNG"))

    if not files:
        return None
    files.sort(key=lambda p: p.stat().st_size, reverse=True)
    return str(files[0])

def make_video(still_path: str, out_path: str, dur=0.7):
    # Tek görselden 0.7s h264 mp4 (30 fps, 1280 genişlik)
    cmd = [
        "ffmpeg","-y","-loop","1","-t",str(dur),"-i",still_path,
        "-vf","scale=1280:-2,format=yuv420p","-r","30",
        "-c:v","libx264","-pix_fmt","yuv420p", out_path
    ]
    subprocess.run(cmd, check=True)

def main():
    missing_letters = []
    for L in LETTERS:
        out = OUT / f"{L}.mp4"
        if out.exists():
            print(f"[SKIP] {L} already exists")
            continue

        letter_dir = find_letter_folder(RAW_ROOT, L)
        if letter_dir is None:
            print(f"[WARN] letter folder not found for {L}")
            missing_letters.append(L)
            continue

        img = pick_image(letter_dir)
        if img is None:
            print(f"[WARN] no images found under {letter_dir} for {L}")
            missing_letters.append(L)
            continue

        try:
            make_video(img, str(out))
            print(f"[OK] {L} -> {out}")
        except Exception as e:
            print(f"[ERR] {L}: {e}")
            missing_letters.append(L)

    if missing_letters:
        print("\nMissing letters:", missing_letters)
        print("Check the following:")
        print("1) Did you download the iCloud placeholder files? (Right click → Download Now)")
        print("2) Did you set RAW_ROOT to the correct folder?")
        print("3) Is the zip fully extracted and are the A–Z folders present?")

if __name__ == "__main__":
    main()

