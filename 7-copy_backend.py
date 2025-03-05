import os
import subprocess
import cloudinary
import cloudinary.uploader
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = "uploads/"
app.config['OUTPUT_FOLDER'] = "processed_files/"
app.config['PYTHON_CMD'] = "python3"  # Use "python" if running in Windows

# Ensure required folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "dzedegcng"),
    api_key=os.getenv("CLOUDINARY_API_KEY", "158983114266962"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", "DK3w8CiFpTfr-T7D5EoA0122s_Q")
)

def upload_to_cloudinary(image_path):
    """Uploads an image to Cloudinary and returns the URL"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    response = cloudinary.uploader.upload(image_path)
    return response["secure_url"]  # Public URL for the uploaded image

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded PDF file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Process the PDF file (running your Python scripts)
    try:
        scripts = [
            "2-convert_pdf_to_excel.py",
            "3-clean_data.py",
            "4-categorize_transactions.py",
            "5-financial_summary.py",
            "6-generate_graphs.py"
        ]

        for script in scripts:
            print(f"🔄 Running: {script}...")  # Start message
            result = subprocess.run([app.config['PYTHON_CMD'], script, file_path], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Error in {script}: {result.stderr}")  # Error message
            raise subprocess.CalledProcessError(result.returncode, script, result.stderr)
    
        print(f"✅ {script} completed successfully!")  # Success message

        # Paths to the generated graphs
        graph_paths = {
            "income_vs_expenses": os.path.join(app.config['OUTPUT_FOLDER'], "monthly_income_vs_expenses.png"),
            "monthly_savings": os.path.join(app.config['OUTPUT_FOLDER'], "monthly_savings.png"),
            "expenses_by_category": os.path.join(app.config['OUTPUT_FOLDER'], "expenses_by_category.png")
        }

        # Upload the graphs to Cloudinary and get their URLs
        graph_urls = {}
        for name, path in graph_paths.items():
            try:
                graph_urls[name] = upload_to_cloudinary(path)
            except FileNotFoundError as e:
                print(f"Graph not found: {e}")
                graph_urls[name] = None

        # Read the financial summary from the generated text file
        summary_file = os.path.join(app.config['OUTPUT_FOLDER'], "financial_summary.txt")
        summary_text = "Summary not available"
        if os.path.exists(summary_file):
            with open(summary_file, "r") as f:
                summary_text = f.read()

        # Return the response with the graphs' URLs and the summary text
        return jsonify({
            "summary_text": summary_text,
            "graphs": graph_urls
        }), 200

    except subprocess.CalledProcessError as e:
        print(f"Error during processing: {e}")
        return jsonify({"error": "Error processing the file", "details": str(e)}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "Unexpected error processing the file"}), 500

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True, port=5001)  # Start the Flask app in debug mode