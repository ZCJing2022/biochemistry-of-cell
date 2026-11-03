from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
archive = root / "source-assets" / "source-figures-v1.zip"
target = root / "assets" / "source-figures"
target.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(archive, "r") as zf:
    for member in zf.namelist():
        if member.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            zf.extract(member, target)
