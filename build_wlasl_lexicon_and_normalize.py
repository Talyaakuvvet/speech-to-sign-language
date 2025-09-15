import json, csv, subprocess
from pathlib import Path

META = Path("wlasl/WLASL_v0.3.json")
SRC_ROOT = Path("clips/ASL/videos")   # senin ham videoların
DST_ROOT = Path("clips/ASL")          # normalize edilmiş gloss dosyaları
DST_ROOT.mkdir(parents=True, exist_ok=True)

LEXICON_CSV = Path("lexicon.csv")

def normalize(src: Path, dst: Path):
    cmd = [
        "ffmpeg","-y","-i",str(src),
        "-r","30","-vf","scale=1280:-2,format=yuv420p",
        "-c:v","libx264","-pix_fmt","yuv420p",
        "-c:a","aac","-shortest",str(dst)
    ]
    subprocess.run(cmd, check=True)

def main():
    data = json.loads(META.read_text())
    seen = set()
    rows = []

    for item in data:
        gloss = item["gloss"].upper().strip()
        for inst in item["instances"]:
            vid = inst["video_id"] + ".mp4"
            src = SRC_ROOT / vid
            if not src.exists():
                continue
            if gloss in seen:
                continue
            dst = DST_ROOT / f"{gloss}.mp4"
            if not dst.exists():
                normalize(src, dst)
            rows.append([gloss, str(dst)])
            seen.add(gloss)
            print(f"[OK] {gloss} -> {dst}")
            break

    # CSV'ye yaz
    with LEXICON_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"\nToplam {len(rows)} gloss lexicon.csv içine yazıldı.")

if __name__ == "__main__":
    main()
