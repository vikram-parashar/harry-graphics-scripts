# WHAT IT DOES:
# - Reads all PDF files from INPUT_FOLDER
# - Each PDF must contain at least 2 pages
# - Creates a subfolder using PDF filename
# - Saves:
#       Page 1 -> front.png
#       Page 2 -> back.png
#
# OUTPUT STRUCTURE:
#
# OUTPUT_FOLDER/
#   file1/
#       front.png
#       back.png
#
#   file2/
#       front.png
#       back.png
#
# =========================================================

from pathlib import Path
import fitz  # PyMuPDF
from tqdm import tqdm

# =========================================================
# USER INPUT
# =========================================================

INPUT_FOLDER = Path(input("Enter INPUT folder path: ").strip('"'))

OUTPUT_FOLDER = Path(input("Enter OUTPUT folder path: ").strip('"'))

DPI = 300  # output image quality

# =========================================================
# DISPLAY SETTINGS
# =========================================================

print("\n" + "=" * 60)
print("PDF FRONT/BACK EXTRACTION SETTINGS")
print("=" * 60)

print(f"INPUT FOLDER  : {INPUT_FOLDER}")
print(f"OUTPUT FOLDER : {OUTPUT_FOLDER}")
print(f"DPI            : {DPI}")
print(f"OUTPUT FORMAT  : PNG")
print(f"FRONT NAME     : front.png")
print(f"BACK NAME      : back.png")

print("=" * 60)

# =========================================================
# VALIDATION
# =========================================================

if not INPUT_FOLDER.exists():
    print("\nERROR: Input folder does not exist.")
    exit()

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# =========================================================
# GET PDF FILES
# =========================================================

pdf_files = list(INPUT_FOLDER.glob("*.pdf"))

if not pdf_files:
    print("\nNo PDF files found.")
    exit()

print(f"\nTOTAL PDF FILES FOUND: {len(pdf_files)}")
print("\nStarting processing...\n")

# =========================================================
# RENDER SETTINGS
# =========================================================

zoom = DPI / 72
matrix = fitz.Matrix(zoom, zoom)

# =========================================================
# PROCESS PDFs
# =========================================================

for pdf_path in tqdm(pdf_files, desc="Processing PDFs", unit="pdf"):

    try:
        # -------------------------------------------------
        # Create folder with PDF filename
        # -------------------------------------------------

        pdf_name = pdf_path.stem

        pdf_output_folder = OUTPUT_FOLDER / pdf_name
        pdf_output_folder.mkdir(parents=True, exist_ok=True)

        # -------------------------------------------------
        # Open PDF
        # -------------------------------------------------

        doc = fitz.open(pdf_path)

        if len(doc) < 2:
            tqdm.write(f"Skipped (<2 pages): {pdf_path.name}")
            doc.close()
            continue

        # -------------------------------------------------
        # PAGE 1 -> front.png
        # -------------------------------------------------

        front_page = doc.load_page(0)

        front_pix = front_page.get_pixmap(matrix=matrix)

        front_output = pdf_output_folder / "front.png"

        front_pix.save(str(front_output))

        # -------------------------------------------------
        # PAGE 2 -> back.png
        # -------------------------------------------------

        back_page = doc.load_page(1)

        back_pix = back_page.get_pixmap(matrix=matrix)

        back_output = pdf_output_folder / "back.png"

        back_pix.save(str(back_output))

        doc.close()

    except Exception as e:
        tqdm.write(f"Error in: {pdf_path.name}")
        tqdm.write(str(e))

# =========================================================
# DONE
# =========================================================

print("\n" + "=" * 60)
print("PROCESS COMPLETED.")
print("=" * 60)