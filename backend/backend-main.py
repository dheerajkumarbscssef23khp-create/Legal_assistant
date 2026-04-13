from flask import Flask, request, jsonify
from flask_cors import CORS
from backend_model import generate_response
from document_praser import extract_text_from_file
import json
import os
from analysis_module import run_analysis # NEW: Import the analysis function

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# NEW: Define the log file path
LOG_FILE = 'usage_log.jsonl'

def log_usage_data(data):
    """Appends usage data to a JSON Lines file for later analysis."""
    # Ensure the duration is converted to float if included
    if 'duration' in data:
        data['duration'] = float(data['duration'])
        
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(data) + '\n')

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_question = data.get("question", "")

    if not user_question:
        return jsonify({"error": "No question provided"}), 400
    
    # NEW: Start timing the response for latency logging
    import time
    start_time = time.time()

    try:
        answer = generate_response(user_question)
        
        # NEW: Log the data after successful response
        end_time = time.time()
        log_usage_data({
            "type": "question",
            "timestamp": time.time(),
            "query_length": len(user_question),
            "response_length": len(answer),
            "duration": end_time - start_time,
            "success": True
        })
        
        return jsonify({"response": answer})
        
    except Exception as e:
        # Log failure
        log_usage_data({
            "type": "question",
            "timestamp": time.time(),
            "query_length": len(user_question),
            "success": False,
            "error": str(e)
        })
        return jsonify({"error": f"Failed to generate response: {e}"}), 500


@app.route("/analyze-document", methods=["POST"])
def analyze_document():
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400
    
    import time
    start_time = time.time()

    try:
        # ❗ FIX: RESET STREAM BEFORE READING
        file.stream.seek(0)
        
        file_size = len(file.read()) # Get file size (bytes)
        file.stream.seek(0) # IMPORTANT: Reset stream again before passing to parser

        extracted_text = extract_text_from_file(file)

        if extracted_text == "Unsupported file format.":
            log_usage_data({"type": "document", "success": False, "reason": "Unsupported format"})
            return jsonify({"error": extracted_text}), 400
        
        if not extracted_text.strip():
            log_usage_data({"type": "document", "success": False, "reason": "Parsing failed"})
            return jsonify({
                "error": "Document parsing failed: Could not extract readable text. It might be a scanned image, encrypted, or the parser failed."
            }), 400

        MAX_TEXT_LENGTH = 30000
        if len(extracted_text) > MAX_TEXT_LENGTH:
            extracted_text = extracted_text[:MAX_TEXT_LENGTH]
            text_length = MAX_TEXT_LENGTH
        else:
            text_length = len(extracted_text)

        answer = generate_response(
            f"Analyze this legal document and explain key points:\n\n{extracted_text}"
        )
        
        # NEW: Log document analysis data
        end_time = time.time()
        log_usage_data({
            "type": "document",
            "timestamp": time.time(),
            "file_size_bytes": file_size,
            "extracted_text_length": text_length,
            "duration": end_time - start_time,
            "success": True
        })
        
        return jsonify({"response": answer})

    except Exception as e:
        log_usage_data({"type": "document", "success": False, "error": str(e)})
        return jsonify({
            "error": f"An unexpected error occurred during processing: {e}. Check library installation (PyPDF2, python-docx)."
        }), 500

# NEW ROUTE: Trigger Data Science Analysis (for demonstration)
@app.route("/run-analysis", methods=["GET"])
def run_ds_analysis():
    # This route triggers the EDA and Model training
    try:
        results = run_analysis(LOG_FILE)
        return jsonify({"message": "Data Science analysis complete.", "results": results}), 200
    except Exception as e:
        return jsonify({"error": f"Analysis failed. Ensure {LOG_FILE} exists and contains data. Details: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)