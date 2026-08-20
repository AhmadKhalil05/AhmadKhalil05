from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import argparse

ROOT = Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser(description="Prepare a portrait for the ASCII renderer.")
parser.add_argument("source", nargs="?", default=str(ROOT / "source" / "profile-photo.png"))
parser.add_argument("--output", default=str(ROOT / "source" / "profile-photo.png"))
args = parser.parse_args()

img = Image.open(args.source).convert("L")
img = ImageOps.autocontrast(img, cutoff=1)
img = ImageEnhance.Contrast(img).enhance(1.4)
img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=140, threshold=2))
img.save(args.output)
print(f"Prepped photo saved to: {args.output}")
