import convertapi
import os

UPLOAD_FOLDER = "uploads/"
OUTPUT_FOLDER = "processed_files/"

# Get the uploaded file (automatically fetch the first PDF)
pdf_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".pdf")]
if not pdf_files:
    print("No PDF found in uploads folder!")
    exit()

# Set the path to the first PDF found in the upload folder
pdf_path = os.path.join(UPLOAD_FOLDER, pdf_files[0])

# You can set the password manually or prompt the user for it
password = "your_pdf_password"  # Replace this with the actual password or prompt the user

# Ensure API Key
convertapi.api_credentials = "secret_viSj4JkvafyxlawY"

# Convert PDF to Excel
print(f"Processing PDF: {pdf_path}")
try:
    convertapi.convert('xlsx', {
        'File': pdf_path,
        'OcrLanguage': 'en',
    }, from_format='pdf').save_files(OUTPUT_FOLDER)
    print("PDF conversion complete!")
except Exception as e:
    print(f"Error during conversion: {e}")