from pathlib import Path

import cv2
from tqdm import tqdm

# =========================================================
# SCRIPT NAME
# =========================================================
# bulk_back_cropper.py
#
# WHAT IT DOES:
# - Reads multiple folders from INPUT_FOLDER
# - Each folder must contain:
#       back.png
#
# - Crops 4 px from ALL SIDES
# - Saves output to OUTPUT_FOLDER
# - Replicates original folder structure
#
# ORIGINAL IMAGE SIZE:
# 637 x 1005 px
#
# OUTPUT IMAGE SIZE:
# 629 x 997 px
#
# =========================================================

# =========================================================
# USER INPUT
# =========================================================

INPUT_FOLDER = Path("/home/vikram/dev/harry-graphics-scripts/out/jaipurGirls1-priview/")

OUTPUT_FOLDER = Path(
    "/home/vikram/dev/harry-graphics-scripts/outbg/jaipurGirls1-priview/"
)

# =========================================================
# SETTINGS
# =========================================================

EXPECTED_WIDTH = 1547
EXPECTED_HEIGHT = 2481

CROP_LEFT = 10
CROP_RIGHT = 10
CROP_TOP = 88
CROP_BOTTOM = 88

OUTPUT_WIDTH = EXPECTED_WIDTH - CROP_LEFT - CROP_RIGHT

OUTPUT_HEIGHT = EXPECTED_HEIGHT - CROP_TOP - CROP_BOTTOM

# =========================================================
# DISPLAY SETTINGS
# =========================================================

print("\n" + "=" * 70)
print("BULK back.png ALL SIDE CROPPER")
print("=" * 70)

print(f"INPUT FOLDER        : {INPUT_FOLDER}")
print(f"OUTPUT FOLDER       : {OUTPUT_FOLDER}")

print("\nORIGINAL SIZE")
print(f"{EXPECTED_WIDTH} x {EXPECTED_HEIGHT} px")

print("\nCROP SETTINGS")
print(f"LEFT                : {CROP_LEFT} px")
print(f"RIGHT               : {CROP_RIGHT} px")
print(f"TOP                 : {CROP_TOP} px")
print(f"BOTTOM              : {CROP_BOTTOM} px")

print("\nOUTPUT SIZE")
print(f"{OUTPUT_WIDTH} x {OUTPUT_HEIGHT} px")

print("=" * 70)

# =========================================================
# VALIDATION
# =========================================================

if not INPUT_FOLDER.exists():
    print("\nERROR: Input folder does not exist.")
    input("Press ENTER to exit...")
    raise SystemExit

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# =========================================================
# GET SUBFOLDERS
# =========================================================

subfolders = [folder for folder in INPUT_FOLDER.iterdir() if folder.is_dir()]

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

for folder in tqdm(subfolders, desc="Processing", unit="folder"):
    try:
        # -------------------------------------------------
        # INPUT FILE
        # -------------------------------------------------

        input_image = folder / "back.png"

        if not input_image.exists():
            tqdm.write(f"Missing back.png : {folder.name}")

            skipped += 1
            continue

        # -------------------------------------------------
        # LOAD IMAGE
        # -------------------------------------------------

        img = cv2.imread(str(input_image), cv2.IMREAD_COLOR)

        if img is None:
            tqdm.write(f"Could not read : {input_image}")

            failed += 1
            continue

        # -------------------------------------------------
        # IMAGE SIZE
        # -------------------------------------------------

        height, width = img.shape[:2]

        # -------------------------------------------------
        # VALIDATE SIZE
        # -------------------------------------------------

        if width != EXPECTED_WIDTH or height != EXPECTED_HEIGHT:
            tqdm.write(f"Unexpected size in {folder.name} : {width}x{height}")

        # -------------------------------------------------
        # SAFETY CHECK
        # -------------------------------------------------

        if width <= (CROP_LEFT + CROP_RIGHT) or height <= (CROP_TOP + CROP_BOTTOM):
            tqdm.write(f"Image too small : {folder.name}")

            failed += 1
            continue

        # -------------------------------------------------
        # CROP IMAGE
        # -------------------------------------------------

        cropped = img[CROP_TOP : height - CROP_BOTTOM, CROP_LEFT : width - CROP_RIGHT]

        # -------------------------------------------------
        # CREATE OUTPUT FOLDER
        # -------------------------------------------------

        output_subfolder = OUTPUT_FOLDER / folder.name

        output_subfolder.mkdir(parents=True, exist_ok=True)

        # -------------------------------------------------
        # OUTPUT FILE
        # -------------------------------------------------

        output_image = output_subfolder / "back.png"

        # -------------------------------------------------
        # SAVE IMAGE
        # -------------------------------------------------

        success = cv2.imwrite(str(output_image), cropped)

        if not success:
            tqdm.write(f"Failed saving : {output_image}")

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

