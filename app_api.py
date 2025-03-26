# app_api.py
from flask import Flask, jsonify, request
import os
from metadata_service import MetadataService
from config import DB_PATH

app = Flask(__name__)

# Define the path for the SQLite database.
metadata_service = MetadataService(DB_PATH)

@app.route('/captures', methods=['GET'])
def list_captures():
    """
    List all available captures.
    """
    captures = metadata_service.list_captures()  # Each record is a tuple: (id, filename, timestamp, status)
    return jsonify(captures), 200

@app.route('/capture/<int:capture_id>/analyze', methods=['POST'])
def analyze_capture(capture_id):
    """
    Trigger analysis on a specific capture.
    For now, this endpoint serves as a stub by updating the capture status.
    """
    capture = metadata_service.get_capture(capture_id)
    if not capture:
        return jsonify({"error": "Capture not found"}), 404

    filename = capture[1]
    
    # Simulate triggering analysis.
    metadata_service.update_status(filename, "analyzing")
    # (Here you might call your analysis app via an HTTP request, message queue, etc.)
    # For now, we immediately mark it as complete.
    metadata_service.update_status(filename, "analysis complete")
    
    return jsonify({"status": "analysis complete", "capture_id": capture_id, "filename": filename}), 200

if __name__ == '__main__':
    # Run the API server on port 5000.
    app.run(debug=True, port=5000)
