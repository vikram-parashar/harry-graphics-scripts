import os
import pandas as pd
from PIL import Image

# Supported image extensions
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".jfif"]

# Root folder containing multiple subfolders
ROOT_DIR = r"/home/vikram/doc/harrygraphics-work/tmp2"


def find_column(columns, starts_with):
    """
    Find first column that starts with given text (case-insensitive)
    """
    for col in columns:
        if str(col).strip().lower().startswith(starts_with.lower()):
            return col
    return None


def find_image(folder, sr_value):
    """
    Find image whose filename starts with SR number
    after trimming and splitting by space.

    Example matches for SR = 12:
        "12.jpg"
        "12 abc.png"
        "12 something.jpeg"

    Non-match:
        "120.jpg"
    """

    sr_str = str(sr_value).strip()

    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)

        if not os.path.isfile(file_path):
            continue

        name, ext = os.path.splitext(file)

        if ext.lower() not in IMAGE_EXTENSIONS:
            continue

        first_part = name.strip().split(".")[0]

        if first_part == sr_str:
            return file_path

    return None


def convert_and_rename_image(src_path, dest_path):
    """
    Convert image to JPG and save
    """
    try:
        with Image.open(src_path) as img:
            rgb_img = img.convert("RGB")
            rgb_img.save(dest_path, "JPEG")
        return True
    except Exception as e:
        print(f"Error converting image {src_path}: {e}")
        return False


def process_folder(folder_path):
    print(f"\nProcessing folder: {folder_path}")

    # Find Excel file
    excel_files = [
        f for f in os.listdir(folder_path) if f.lower().endswith((".xlsx", ".xls"))
    ]

    if not excel_files:
        print("No Excel file found.")
        return

    excel_path = os.path.join(folder_path, excel_files[0])

    try:
        df = pd.read_excel(excel_path, skiprows=2)
    except Exception as e:
        print(f"Could not read Excel: {e}")
        return

    # Find required columns
    sr_col = find_column(df.columns, "sr")
    std_col = find_column(df.columns, "std")

    if not sr_col:
        print("No column starting with 'Sr' found.")
        return

    if not std_col:
        print("No column starting with 'Std' found.")
        return

    print(f"Using SR column : {sr_col}")
    print(f"Using STD column: {std_col}")

    photo_numbers = []

    for idx, row in df.iterrows():
        sr = row[sr_col]
        std = row[std_col]

        if pd.isna(sr) or pd.isna(std):
            photo_numbers.append("")
            continue

        try:
            sr_int = int(float(sr))
        except:
            print(f"Invalid SR at row {idx + 2}")
            photo_numbers.append("")
            continue

        std_clean = str(std).replace(" ", "")
        new_name = f"{std_clean}-{5000 + sr_int}"
        photo_numbers.append(new_name)

        # Find matching image
        image_path = find_image(folder_path, sr_int)

        if not image_path:
            print(f"Image not found for SR: {sr_int}")
            continue

        new_image_path = os.path.join(folder_path, f"{new_name}.jpg")

        success = convert_and_rename_image(image_path, new_image_path)

        if success:
            print(f"Saved: {new_name}.jpg")

            # Remove old image if different
            if os.path.abspath(image_path) != os.path.abspath(new_image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Could not remove old image: {e}")

    # Add/update PhotoNo column
    df["PhotoNo"] = photo_numbers

    # Save updated Excel
    updated_excel = os.path.join(folder_path, excel_files[0])

    try:
        df.to_excel(updated_excel, index=False)
        print(f"Updated Excel saved: {updated_excel}")
    except Exception as e:
        print(f"Error saving Excel: {e}")


def main():
    for item in os.listdir(ROOT_DIR):
        folder_path = os.path.join(ROOT_DIR, item)

        if os.path.isdir(folder_path):
            process_folder(folder_path)

    print("\nDone.")


if __name__ == "__main__":
    main()
