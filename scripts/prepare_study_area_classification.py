"""Extract the four complete map panels from the verified legacy composite."""

from hashlib import sha256
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "legacy/figures/four_site_classification/four_site_maize_soybean.png"
OUTPUT = ROOT / "figures/study_area"
SOURCE_SHA256 = "4f28e3d8bfb490122fa53066e07f759b1ed2965b97004b02f55f234f73cdd5a2"
PANELS = {
    "A": (134, 134, 3052, 3052),
    "B": (3325, 134, 6243, 3052),
    "C": (134, 3365, 3052, 6283),
    "D": (3325, 3365, 6243, 6283),
}


def main() -> None:
    if sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError("The source image differs from the verified composite")
    with Image.open(SOURCE) as image:
        if image.size != (6377, 7122):
            raise ValueError(f"Unexpected source image size: {image.size}")
        for site, box in PANELS.items():
            image.crop(box).save(OUTPUT / f"fig_study_area_{site}.png")


if __name__ == "__main__":
    main()
