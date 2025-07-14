#!/usr/bin/env python3
import os
from flask import Flask, render_template, request, send_file, jsonify

from downloader import download_video
from file_utils import create_ascii_filename, create_content_disposition_header

app = Flask(__name__)

# Application settings
DEFAULT_DOWNLOAD_DIR = '/app/downloads'
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8080

DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', DEFAULT_DOWNLOAD_DIR)
HOST = os.getenv('HOST', DEFAULT_HOST)
PORT = int(os.getenv('PORT', DEFAULT_PORT))

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


def create_download_response(file_path, filename):
    """Create download response"""
    ascii_filename = create_ascii_filename(filename)

    response = send_file(
        file_path,
        as_attachment=True,
        download_name=ascii_filename,
        mimetype='application/octet-stream'
    )

    # Manually set Content-Disposition header (RFC 5987 compliant)
    # Override Flask's default header to support Japanese filenames properly
    response.headers['Content-Disposition'] = create_content_disposition_header(filename, ascii_filename)

    return response


@app.route('/download', methods=['POST'])
def download():
    """Download processing"""
    try:
        url = request.form.get('url')
        format_type = request.form.get('format')

        if not url or not format_type:
            return jsonify({'error': 'URLと形式を指定してください'}), 400

        # Execute download
        file_path, filename = download_video(url, format_type, DOWNLOAD_DIR)

        # Create response
        return create_download_response(file_path, filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=False)

