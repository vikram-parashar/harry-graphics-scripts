from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

# =========================================================
# SCRIPT NAME
# =========================================================
# image_to_pdf_with_filename_text.py
#
# WHAT IT DOES:
# - Reads all images from an input folder
# - Adds filename text at top center
# - Creates a single PDF from all images
#
# TEXT AREA:
# - y1 = 32
# - y2 = 90
#
# IMAGE SIZE EXPECTED:
# - 3600 x 5400 px
#
# OUTPUT:
# - <input_folder_name>.pdf
#
# =========================================================

# =========================================================
# USER INPUT
# =========================================================

INPUT_DIR = Path(
    "/home/vikram/dev/harry-graphics-scripts/tiles/udaipurwati/back"
)

# =========================================================
# CONFIG
# =========================================================

SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}

TEXT_PREFIX = "UDAIPURWATI"

TEXT_Y1 = 32
TEXT_Y2 = 90

IMAGE_W = 3600
IMAGE_H = 5400

FONT_SIZE = 42

TEXT_COLOR = "black"

DPI = 300

# =========================================================
# LOAD IMAGES
# =========================================================

if not INPUT_DIR.exists():
    print("ERROR: Input folder does not exist.")
    exit()

image_files = sorted(
    [
        p
        for p in INPUT_DIR.iterdir()
        if p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
)

if not image_files:
    print("ERROR: No images found.")
    exit()

# =========================================================
# FONT
# =========================================================

try:
    FONT = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        FONT_SIZE,
    )
except Exception:
    FONT = ImageFont.load_default()

# =========================================================
# PROCESS IMAGES
# =========================================================

processed_images = []

text_center_y = (TEXT_Y1 + TEXT_Y2) // 2

total_images = len(image_files)

print(f"\nFound {total_images} images\n")

for index, img_path in enumerate(
    tqdm(image_files, desc="Processing Images"),
    start=1,
):
    img = Image.open(img_path).convert("RGB")

    # -----------------------------------------------------
    # Optional validation
    # -----------------------------------------------------

    if img.size != (IMAGE_W, IMAGE_H):
        print(
            f"\nWARNING: {img_path.name} size is {img.size}, "
            f"expected {(IMAGE_W, IMAGE_H)}"
        )

    draw = ImageDraw.Draw(img)

    # -----------------------------------------------------
    # TEXT
    # -----------------------------------------------------

    text = f"{TEXT_PREFIX} {img_path.stem}/{total_images}"

    # -----------------------------------------------------
    # Measure text
    # -----------------------------------------------------

    bbox = draw.textbbox((0, 0), text, font=FONT)

    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # -----------------------------------------------------
    # Center horizontally
    # -----------------------------------------------------

    x = (img.width - text_w) // 2

    # -----------------------------------------------------
    # Center vertically between y1 and y2
    # -----------------------------------------------------

    y = text_center_y - (text_h // 2)

    # -----------------------------------------------------
    # Draw text
    # -----------------------------------------------------

    draw.text(
        (x, y),
        text,
        fill=TEXT_COLOR,
        font=FONT,
    )

    processed_images.append(img)

# =========================================================
# SAVE PDF
# =========================================================

output_pdf = INPUT_DIR.parent / f"{INPUT_DIR.name}.pdf"

first_image = processed_images[0]

remaining_images = processed_images[1:]

print("\nGenerating PDF...\n")

first_image.save(
    output_pdf,
    "PDF",
    save_all=True,
    append_images=remaining_images,
    resolution=DPI,
)

# =========================================================
# DONE
# =========================================================

print("\n" + "=" * 60)
print("PDF CREATED SUCCESSFULLY")
print("=" * 60)

print(f"\nSaved PDF:")
print(output_pdf)
