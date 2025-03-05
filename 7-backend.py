import os
import requests
import cloudinary
import cloudinary.uploader
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)
UPLOAD_FOLDER = "uploads/"
OUTPUT_FOLDER = "processed_files/"
PYTHON_CMD = "python3"  # Use "python" if running in Windows

# Ensure required folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ✅ Configure Cloudinary
cloudinary.config(
    cloud_name="dzedegcng",  # Replace with your Cloudinary Cloud Name
    api_key="158983114266962",  # Replace with your Cloudinary API Key
    api_secret="DK3w8CiFpTfr-T7D5EoA0122s_Q"  # Replace with your Cloudinary API Secret
)

def upload_to_cloudinary(image_path):
    """Uploads an image to Cloudinary and returns the URL"""
    response = cloudinary.uploader.upload(image_path)
    return response["secure_url"]  # Public URL for the uploaded image

def download_pdf(pdf_url, save_path):
    """Downloads a PDF from a URL and saves it locally"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}  # Some servers block unknown requests
        response = requests.get(pdf_url, headers=headers, stream=True)

        if response.status_code != 200:
            print(f"❌ Failed to download. Status code: {response.status_code}")
            return False

        # Ensure it's a PDF by checking headers
        content_type = response.headers.get("Content-Type", "")
        if "pdf" not in content_type:
            print(f"⚠️ Warning: Content-Type is {content_type}, not a PDF!")
        
        # If the file has no extension, add '.pdf'
        if not save_path.endswith(".pdf"):
            save_path += ".pdf"

        with open(save_path, "wb") as pdf_file:
            for chunk in response.iter_content(chunk_size=8192):
                pdf_file.write(chunk)

        print(f"✅ PDF downloaded successfully: {save_path}")
        return True

    except requests.RequestException as e:
        print(f"Error downloading PDF: {e}")
        return False


@app.route('/upload', methods=['POST'])
def upload_file():
    data = request.json  # Get JSON data
    if "pdf_url" not in data:
        return jsonify({"error": "Missing 'pdf_url' in request"}), 400

    pdf_url = data["pdf_url"]
    pdf_password = data.get("password", "")  # Get password (default: empty string)

    pdf_filename = pdf_url.split("/")[-1]  # Extract filename from URL
    temp_pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)

    # Download the PDF from the URL
    if not download_pdf(pdf_url, temp_pdf_path):
        return jsonify({"error": "Failed to download the PDF"}), 400

    # 🔥 Pass the password to convert PDF to Excel script
    try:
        subprocess.run([PYTHON_CMD, "2-convert_pdf_to_excel.py", temp_pdf_path, pdf_password], check=True)
        subprocess.run([PYTHON_CMD, "3-clean_data.py"], check=True)
        subprocess.run([PYTHON_CMD, "4-categorize_transactions.py"], check=True)
        subprocess.run([PYTHON_CMD, "5-financial_summary.py"], check=True)
        subprocess.run([PYTHON_CMD, "6-generate_graphs.py"], check=True)

        # Paths to the generated graphs
        graph_paths = {
            "income_vs_expenses": os.path.join(OUTPUT_FOLDER, "monthly_income_vs_expenses.png"),
            "monthly_savings": os.path.join(OUTPUT_FOLDER, "monthly_savings.png"),
            "expenses_by_category": os.path.join(OUTPUT_FOLDER, "expenses_by_category.png")
        }

        # Upload graphs to Cloudinary & get URLs
        graph_urls = {name: upload_to_cloudinary(path) for name, path in graph_paths.items()}

        # Read financial summary from the generated text file
        summary_file = os.path.join(OUTPUT_FOLDER, "financial_summary.txt")
        summary_text = "Summary not available"
        if os.path.exists(summary_file):
            with open(summary_file, "r") as f:
                summary_text = f.read()

        # Return JSON response with financial summary & image URLs
        return jsonify({
            "summary_text": summary_text,
            "graphs": graph_urls
        }), 200

    except subprocess.CalledProcessError as e:
        print(f"Error in subprocess execution: {e}")
        return jsonify({"error": "Error processing the PDF"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
