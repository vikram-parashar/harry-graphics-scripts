from pathlib import Path
import pandas as pd

INPUT_DIR = Path("/home/vikram/doc/harrygraphics-work/3rd slot ID CARD 2026-27")
OUTPUT_FILE = Path("combined_students.xlsx")

# Standard column mapping
COLUMN_PATTERNS = {
    "student name": "student",
    "blood group": "blood",
    "dob": "dob",
    "contact no.": "contact",
    "mode of transport": "mode",
    "class": "std",
    "photo no.": "photo",
    "house": "house",
}

combined_data = []
errors = []


def normalize_col(col_name: str) -> str:
    return str(col_name).strip().lower()


def find_matching_column(columns, starts_with):
    for col in columns:
        if normalize_col(col).startswith(starts_with):
            return col
    return None


excel_files = list(INPUT_DIR.rglob("*.xlsx")) + list(INPUT_DIR.rglob("*.xls"))

if not excel_files:
    print("ERROR: No Excel files found.")
    raise SystemExit(1)

for file_path in excel_files:
    try:
        df = pd.read_excel(file_path)

        mapped_columns = {}

        for target_col, prefix in COLUMN_PATTERNS.items():
            matched_col = find_matching_column(df.columns, prefix)

            if matched_col is None:
                errors.append(f"{file_path}: Missing column starting with '{prefix}'")
            else:
                mapped_columns[target_col] = matched_col

        if not mapped_columns:
            errors.append(f"{file_path}: No matching columns found")
            continue

        temp_df = pd.DataFrame()

        for target_col in COLUMN_PATTERNS.keys():
            source_col = mapped_columns.get(target_col)

            if source_col:
                temp_df[target_col] = df[source_col]
            else:
                temp_df[target_col] = None

        combined_data.append(temp_df)

    except Exception as e:
        errors.append(f"{file_path}: {str(e)}")

if errors:
    for err in errors:
        print(f"ERROR: {err}")
else:
    try:
        final_df = pd.concat(combined_data, ignore_index=True)
        final_df.to_excel(OUTPUT_FILE, index=False)
    except Exception as e:
        print(f"ERROR: Failed to save output file: {e}")
