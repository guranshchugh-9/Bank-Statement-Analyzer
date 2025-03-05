import pandas as pd
import os

OUTPUT_FOLDER = "processed_files/"
excel_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".xlsx")]

if not excel_files:
    print("No Excel file found in processed folder!")
    exit()

excel_file = os.path.join(OUTPUT_FOLDER, excel_files[0])

# Read all sheets first
all_sheets = pd.read_excel(excel_file, sheet_name=None, engine="openpyxl", header=None)

# Get the first sheet to extract headers
first_sheet_name = list(all_sheets.keys())[0]
first_sheet = all_sheets[first_sheet_name]

column_names = first_sheet.columns.tolist()

# Find the header row in the first sheet
# header_row_idx = None
# for idx, row in first_sheet.iterrows():
#     if row.notna().sum() >= 3:  # At least 3 non-null values to be considered a header
#         header_row_idx = idx
#         column_names = row.tolist()
#         break

if column_names is None:
    print("Could not find valid headers in the first sheet!")
    exit()

def clean_table(df, column_names):
    # Drop completely empty rows
    df = df.dropna(how='all')
    
    # Assign column names
    # if len(df.columns) != len(column_names):
    #     # Pad or truncate columns to match the expected number
    #     if len(df.columns) < len(column_names):
    #         for i in range(len(df.columns), len(column_names)):
    #             df[i] = None
    #     df = df.iloc[:, :len(column_names)]
    
    df.columns = column_names
    
    cleaned_rows = []
    current_row = None
    
    for _, row in df.iterrows():
        # Check if this is a new transaction (has a date)
        if pd.notna(row['Date']):
            if current_row is not None:
                cleaned_rows.append(current_row)
            current_row = row.copy()
        else:
            # This is a continuation of the narration
            if current_row is not None and pd.notna(row['Narration']):
                current_narration = str(current_row['Narration']).strip()
                additional_narration = str(row['Narration']).strip()
                if additional_narration:  # Only append if there's actual content
                    current_row['Narration'] = f"{current_narration} {additional_narration}"
    
    # Don't forget to append the last row
    if current_row is not None:
        cleaned_rows.append(current_row)
    
    return pd.DataFrame(cleaned_rows)

# Process all sheets
cleaned_tables = []
for sheet_name, df in all_sheets.items():
    if sheet_name == first_sheet_name:
        # For first sheet, skip the header row
        df = df.iloc[1:]
    
    cleaned_df = clean_table(df, column_names)
    if not cleaned_df.empty:
        cleaned_tables.append(cleaned_df)

# Combine all cleaned tables
if cleaned_tables:
    combined_df = pd.concat(cleaned_tables, ignore_index=True)
    
    # Sort by date if date column exists
    if 'Date' in combined_df.columns:
        combined_df['Date'] = pd.to_datetime(combined_df['Date'], errors='coerce')
        combined_df = combined_df.sort_values('Date')

    # Save to CSV
    csv_output = os.path.join(OUTPUT_FOLDER, "cleaned_bank_statement.csv")
    combined_df.to_csv(csv_output, index=False)
    print(f"Cleaned data saved to: {csv_output}")
else:
    print("No valid data found in any sheet!")