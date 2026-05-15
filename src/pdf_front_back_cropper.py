from pathlib import Path

import fitz  # PyMuPDF
import cv2
import numpy as np
from tqdm import tqdm

# =========================================================
# SCRIPT NAME
# =========================================================
# pdf_front_back_cropper.py
#
# WHAT IT DOES:
# - Reads all PDFs from INPUT_FOLDER
# - Renders first page at selected DPI
# - Crops FRONT and BACK regions using MM coordinates
# - Creates a folder using PDF filename
# - Saves:
#       front.png
#       back.png
#
# OUTPUT STRUCTURE:
#
# OUTPUT_FOLDER/
#   PDF_NAME/
#       front.png
#       back.png
#
# =========================================================

# =========================================================
# USER INPUT
# =========================================================

INPUT_FOLDER = Path(
    input("Enter INPUT folder path: ").strip('"')
)

OUTPUT_FOLDER = Path(
    input("Enter OUTPUT folder path: ").strip('"')
)

# =========================================================
# CONFIG
# =========================================================

dpi = 600

# FRONT CROP AREA
FRONT_COORDS_MM = {
    "x1": 12,
    "y1": 11,
    "x2": 77,
    "y2": 114
}

# BACK CROP AREA
BACK_COORDS_MM = {
    "x1": 86.5,
    "y1": 11,
    "x2": 152,
    "y2": 116
}

# =========================================================
# DISPLAY SETTINGS
# =========================================================

print("\n" + "=" * 70)
print("PDF FRONT/BACK CROP SETTINGS")
print("=" * 70)

print(f"INPUT FOLDER      : {INPUT_FOLDER}")
print(f"OUTPUT FOLDER     : {OUTPUT_FOLDER}")
print(f"DPI                : {dpi}")

print("\nFRONT CROP (MM)")
for k, v in FRONT_COORDS_MM.items():
    print(f"  {k} = {v}")

print("\nBACK CROP (MM)")
for k, v in BACK_COORDS_MM.items():
    print(f"  {k} = {v}")

print("\nOUTPUT STRUCTURE")
print("OUTPUT_FOLDER/")
print("  PDF_NAME/")
print("      front.png")
print("      back.png")

print("=" * 70)

# =========================================================
# VALIDATION
# =========================================================

if not INPUT_FOLDER.exists():
    print("\nERROR: Input folder does not exist.")
    input("Press ENTER to exit...")
    exit()

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

pdf_files = sorted(
    INPUT_FOLDER.glob("*.pdf")
)

if not pdf_files:
    print("\nERROR: No PDF files found.")
    input("Press ENTER to exit...")
    exit()

print(f"\nTOTAL PDF FILES FOUND: {len(pdf_files)}")
print("\nStarting processing...\n")

# =========================================================
# HELPERS
# =========================================================

MM_PER_INCH = 25.4
PX_PER_MM = dpi / MM_PER_INCH


def mm_to_px(mm):
    return int(mm * PX_PER_MM)


def crop_mm(img, coords):

    x1 = mm_to_px(coords["x1"])
    y1 = mm_to_px(coords["y1"])
    x2 = mm_to_px(coords["x2"])
    y2 = mm_to_px(coords["y2"])

    return img[y1:y2, x1:x2]


def pdf_page_to_cv2(
    pdf_path: Path,
    page_number=0,
    dpi=600
):

    doc = fitz.open(pdf_path)

    page = doc[page_number]

    pix = page.get_pixmap(dpi=dpi)

    img = np.frombuffer(
        pix.samples,
        dtype=np.uint8
    )

    img = img.reshape(
        pix.height,
        pix.width,
        pix.n
    )

    if pix.n == 4:
        img = cv2.cvtColor(
            img,
            cv2.COLOR_RGBA2BGR
        )
    else:
        img = cv2.cvtColor(
            img,
            cv2.COLOR_RGB2BGR
        )

    doc.close()

    return img


def process_pdf(pdf_path: Path):

    # -----------------------------------------------------
    # Convert PDF page to image
    # -----------------------------------------------------

    img = pdf_page_to_cv2(
        pdf_path,
        dpi=dpi
    )

    # -----------------------------------------------------
    # Crop front and back
    # -----------------------------------------------------

    front = crop_mm(
        img,
        FRONT_COORDS_MM
    )

    back = crop_mm(
        img,
        BACK_COORDS_MM
    )

    # -----------------------------------------------------
    # Create folder using PDF name
    # -----------------------------------------------------

    pdf_name = pdf_path.stem

    pdf_output_folder = OUTPUT_FOLDER / pdf_name

    pdf_output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Save files
    # -----------------------------------------------------

    front_path = pdf_output_folder / "front.png"
    back_path = pdf_output_folder / "back.png"

    cv2.imwrite(str(front_path), front)
    cv2.imwrite(str(back_path), back)


# =========================================================
# MAIN PROCESS
# =========================================================

for pdf_path in tqdm(
    pdf_files,
    desc="Processing PDFs",
    unit="pdf"
):

    try:
        process_pdf(pdf_path)

    except Exception as e:
        tqdm.write(f"ERROR: {pdf_path.name}")
        tqdm.write(str(e))

# =========================================================
# DONE
# =========================================================

print("\n" + "=" * 70)
print("PROCESS COMPLETED.")
print("=" * 70)

input("\nPress ENTER to exit...")