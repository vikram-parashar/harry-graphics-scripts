from pathlib import Path
from PIL import Image

# =========================
# CONFIG
# =========================

INPUT_DIR = "/home/vikram/Downloads/sample/"  # Folder containing multiple subfolders
OUTPUT_DIR = "out"  # Output folder
BG_IMAGE_PATH = "/home/vikram/Downloads/bg.jpeg"  # Background image you provide

# DPI used for mm -> pixels conversion
DPI = 300

# Sizes in mm
BG_SIZE_MM = (55, 87)
BACK_SIZE_MM = (52, 82)


# =========================
# HELPERS
# =========================


def mm_to_px(mm, dpi=DPI):
    return int((mm / 25.4) * dpi)


def size_mm_to_px(size_mm):
    return (
        mm_to_px(size_mm[0]),
        mm_to_px(size_mm[1]),
    )


# =========================
# PREPARE SIZES
# =========================

bg_size_px = size_mm_to_px(BG_SIZE_MM)
back_size_px = size_mm_to_px(BACK_SIZE_MM)

print(f"Background size (px): {bg_size_px}")
print(f"Back image size (px): {back_size_px}")


# =========================
# LOAD & RESIZE BG
# =========================

bg_base = Image.open(BG_IMAGE_PATH).convert("RGBA")
bg_base = bg_base.resize(bg_size_px, Image.LANCZOS)


# =========================
# PROCESS ALL FOLDERS
# =========================

input_path = Path(INPUT_DIR)
output_path = Path(OUTPUT_DIR)

for folder in input_path.iterdir():
    if not folder.is_dir():
        continue

    back_path = folder / "back.png"

    if not back_path.exists():
        print(f"Skipping: {folder} (no back.png)")
        continue

    print(f"Processing: {folder.name}")

    # Load and resize back.png
    back_img = Image.open(back_path).convert("RGBA")
    back_img = back_img.resize(back_size_px, Image.LANCZOS)

    # Copy background
    final_img = bg_base.copy()

    # Center position
    x = (bg_size_px[0] - back_size_px[0]) // 2
    y = (bg_size_px[1] - back_size_px[1]) // 2

    # Paste centered
    final_img.paste(back_img, (x, y), back_img)

    # Create output folder
    out_folder = output_path / folder.name
    out_folder.mkdir(parents=True, exist_ok=True)

    # Save updated back.png
    out_file = out_folder / "back.png"
    final_img.save(out_file)

    print(f"Saved -> {out_file}")

print("Done.")
