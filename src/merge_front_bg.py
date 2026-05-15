from pathlib import Path

import cv2
from tqdm import tqdm

# =========================================================
# SCRIPT NAME
# =========================================================
# bulk_front_bg_merger.py
#
# WHAT IT DOES:
# - Takes a BACKGROUND image as input
# - Reads multiple folders from INPUT_FOLDER
# - Each folder must contain:
#       front.png
#
# - Resizes front.png to 421 x 660 px
# - Places it on background image
# - Placement offset:
#       X = 6 px
#       Y = 22 px
#
# - Saves result in OUTPUT_FOLDER
# - Replicates original folder structure
#
# BACKGROUND SIZE:
# 433 x 685 px
#
# =========================================================

# =========================================================
# USER INPUT
# =========================================================

BG_IMAGE_PATH = Path("/home/vikram/dev/harry-graphics-scripts/in/bg.png")

INPUT_FOLDER = Path(
    "/home/vikram/dev/harry-graphics-scripts/out/jaipurGirls1-civilline/"
)

OUTPUT_FOLDER = Path(
    "/home/vikram/dev/harry-graphics-scripts/outbg/jaipurGirls1-civilline/"
)

# =========================================================
# SETTINGS
# =========================================================

# Background size

BG_WIDTH = 433 * 3
BG_HEIGHT = 685 * 3

# Front image stretched size

FRONT_WIDTH = 421 * 3
FRONT_HEIGHT = 660 * 3

# Placement position

PASTE_X = 6 * 3
PASTE_Y = 22 * 3

# =========================================================
# DISPLAY SETTINGS
# =========================================================

print("\n" + "=" * 70)
print("BULK FRONT + BACKGROUND MERGER")
print("=" * 70)

print(f"BACKGROUND IMAGE    : {BG_IMAGE_PATH}")
print(f"INPUT FOLDER        : {INPUT_FOLDER}")
print(f"OUTPUT FOLDER       : {OUTPUT_FOLDER}")

print("\nBACKGROUND SIZE")
print(f"{BG_WIDTH} x {BG_HEIGHT} px")

print("\nFRONT SIZE")
print(f"{FRONT_WIDTH} x {FRONT_HEIGHT} px")

print("\nPLACEMENT")
print(f"X OFFSET            : {PASTE_X} px")
print(f"Y OFFSET            : {PASTE_Y} px")

print("=" * 70)

# =========================================================
# VALIDATION
# =========================================================

bg_path = Path(BG_IMAGE_PATH)

if not bg_path.exists():
    print("\nERROR: Background image does not exist.")
    input("Press ENTER to exit...")
    raise SystemExit

if not INPUT_FOLDER.exists():
    print("\nERROR: Input folder does not exist.")
    input("Press ENTER to exit...")
    raise SystemExit

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# =========================================================
# LOAD BACKGROUND IMAGE
# =========================================================

bg_img = cv2.imread(str(bg_path), cv2.IMREAD_UNCHANGED)

if bg_img is None:
    print("\nERROR: Could not read background image.")
    input("Press ENTER to exit...")
    raise SystemExit

# ---------------------------------------------------------
# FORCE BACKGROUND SIZE
# ---------------------------------------------------------

bg_img = cv2.resize(bg_img, (BG_WIDTH, BG_HEIGHT), interpolation=cv2.INTER_LINEAR)

# =========================================================
# GET ALL SUBFOLDERS
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
        # FRONT IMAGE
        # -------------------------------------------------

        front_path = folder / "front.png"

        if not front_path.exists():
            tqdm.write(f"Missing front.png : {folder.name}")

            skipped += 1
            continue

        # -------------------------------------------------
        # LOAD FRONT IMAGE
        # -------------------------------------------------

        front_img = cv2.imread(str(front_path), cv2.IMREAD_UNCHANGED)

        if front_img is None:
            tqdm.write(f"Could not read : {front_path}")

            failed += 1
            continue

        # -------------------------------------------------
        # STRETCH FRONT IMAGE
        # -------------------------------------------------

        front_img = cv2.resize(
            front_img, (FRONT_WIDTH, FRONT_HEIGHT), interpolation=cv2.INTER_LINEAR
        )

        # -------------------------------------------------
        # COPY BACKGROUND
        # -------------------------------------------------

        final_img = bg_img.copy()

        # -------------------------------------------------
        # SAFETY CHECK
        # -------------------------------------------------

        if PASTE_X + FRONT_WIDTH > BG_WIDTH or PASTE_Y + FRONT_HEIGHT > BG_HEIGHT:
            tqdm.write(f"Front image exceeds background : {folder.name}")

            failed += 1
            continue

        # -------------------------------------------------
        # PASTE FRONT IMAGE
        # -------------------------------------------------

        final_img[PASTE_Y : PASTE_Y + FRONT_HEIGHT, PASTE_X : PASTE_X + FRONT_WIDTH] = (
            front_img
        )

        # -------------------------------------------------
        # CREATE OUTPUT FOLDER
        # -------------------------------------------------

        output_subfolder = OUTPUT_FOLDER / folder.name

        output_subfolder.mkdir(parents=True, exist_ok=True)

        # -------------------------------------------------
        # OUTPUT FILE
        # -------------------------------------------------

        output_file = output_subfolder / "front.png"

        # -------------------------------------------------
        # SAVE OUTPUT
        # -------------------------------------------------

        success = cv2.imwrite(str(output_file), final_img)

        if not success:
            tqdm.write(f"Failed saving : {output_file}")

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

