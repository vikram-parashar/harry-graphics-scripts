from pathlib import Path

import cv2
from tqdm import tqdm

# =========================================================
# SCRIPT NAME
# =========================================================
# bulk_front_top_cropper_55px.py
#
# WHAT IT DOES:
# - Reads multiple folders from INPUT_FOLDER
# - Each folder must contain:
#       front.png
#
# - Crops 55 px from TOP of front.png
# - Saves output to OUTPUT_FOLDER
# - Replicates original folder structure
#
# ORIGINAL IMAGE SIZE:
# 1855 x 2918 px
#
# OUTPUT IMAGE SIZE:
# 1855 x 2863 px
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
# SETTINGS
# =========================================================

TOP_CROP_PX = 13

EXPECTED_WIDTH = 1855
EXPECTED_HEIGHT = 2918

OUTPUT_HEIGHT = EXPECTED_HEIGHT - TOP_CROP_PX

# =========================================================
# DISPLAY SETTINGS
# =========================================================

print("\n" + "=" * 70)
print("BULK FRONT.PNG TOP CROPPER")
print("=" * 70)

print(f"INPUT FOLDER        : {INPUT_FOLDER}")
print(f"OUTPUT FOLDER       : {OUTPUT_FOLDER}")

print("\nORIGINAL SIZE")
print(f"{EXPECTED_WIDTH} x {EXPECTED_HEIGHT} px")

print("\nTOP CROP")
print(f"{TOP_CROP_PX} px")

print("\nOUTPUT SIZE")
print(f"{EXPECTED_WIDTH} x {OUTPUT_HEIGHT} px")

print("=" * 70)

# =========================================================
# VALIDATION
# =========================================================

if not INPUT_FOLDER.exists():

    print("\nERROR: Input folder does not exist.")
    input("Press ENTER to exit...")
    raise SystemExit

OUTPUT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

# =========================================================
# GET ALL SUBFOLDERS
# =========================================================

subfolders = [
    folder for folder in INPUT_FOLDER.iterdir()
    if folder.is_dir()
]

if not subfolders:

    print("\nERROR: No subfolders found.")
    input("Press ENTER to exit...")
    raise SystemExit

print(f"\nTOTAL FOLDERS FOUND: {len(subfolders)}")
print("\nStarting processing...\n")

# =========================================================
# COUNTERS
# =========================================================

processed = 0
skipped = 0
failed = 0

# =========================================================
# MAIN PROCESS
# =========================================================

for folder in tqdm(
    subfolders,
    desc="Processing",
    unit="folder"
):

    try:

        # -------------------------------------------------
        # INPUT FILE
        # -------------------------------------------------

        input_image = folder / "front.png"

        if not input_image.exists():

            tqdm.write(
                f"Missing front.png : {folder.name}"
            )

            skipped += 1
            continue

        # -------------------------------------------------
        # LOAD IMAGE
        # -------------------------------------------------

        img = cv2.imread(str(input_image))

        if img is None:

            tqdm.write(
                f"Could not read : {input_image}"
            )

            failed += 1
            continue

        # -------------------------------------------------
        # IMAGE SIZE
        # -------------------------------------------------

        height, width = img.shape[:2]

        # -------------------------------------------------
        # VALIDATE SIZE
        # -------------------------------------------------

        if (
            width != EXPECTED_WIDTH
            or
            height != EXPECTED_HEIGHT
        ):

            tqdm.write(
                f"Unexpected size in {folder.name} : "
                f"{width}x{height}"
            )

        # -------------------------------------------------
        # SAFETY CHECK
        # -------------------------------------------------

        if height <= TOP_CROP_PX:

            tqdm.write(
                f"Image height too small : {folder.name}"
            )

            failed += 1
            continue

        # -------------------------------------------------
        # CROP TOP 55 PX
        # -------------------------------------------------

        cropped = img[
            TOP_CROP_PX:,
            :
        ]

        # -------------------------------------------------
        # CREATE OUTPUT FOLDER
        # -------------------------------------------------

        output_subfolder = OUTPUT_FOLDER / folder.name

        output_subfolder.mkdir(
            parents=True,
            exist_ok=True
        )

        # -------------------------------------------------
        # OUTPUT FILE
        # -------------------------------------------------

        output_image = output_subfolder / "front.png"

        # -------------------------------------------------
        # SAVE IMAGE
        # -------------------------------------------------

        success = cv2.imwrite(
            str(output_image),
            cropped
        )

        if not success:

            tqdm.write(
                f"Failed saving : {output_image}"
            )

            failed += 1
            continue

        processed += 1

    except Exception as e:

        tqdm.write(f"ERROR : {folder.name}")
        tqdm.write(str(e))

        failed += 1

# =========================================================
# DONE
# =========================================================

print("\n" + "=" * 70)
print("PROCESS COMPLETED")
print("=" * 70)

print(f"PROCESSED : {processed}")
print(f"SKIPPED   : {skipped}")
print(f"FAILED    : {failed}")

print("=" * 70)

input("\nPress ENTER to exit...")