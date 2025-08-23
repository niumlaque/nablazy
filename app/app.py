#!/usr/bin/env python3
from typing import Tuple, Union
import os
from flask import Flask, render_template, request, send_file, jsonify, Response

from downloader import download_video
from file_utils import create_ascii_filename, create_content_disposition_header


class App:
    flask_app: Flask
    default_download_dir: str
    default_host: str
    default_port: int
    download_dir: str
    host: str
    port: int

    def __init__(self) -> None:
        self.flask_app = Flask(__name__)

        self.default_download_dir = "/app/downloads"
        self.default_host = "0.0.0.0"
        self.default_port = 8080

        self.download_dir = os.getenv("DOWNLOAD_DIR", self.default_download_dir)
        self.host = os.getenv("HOST", self.default_host)
        self.port = int(os.getenv("PORT", self.default_port))

        os.makedirs(self.download_dir, exist_ok=True)

        self._setup_routes()

    def _setup_routes(self) -> None:
        """Setup Flask routes"""
        self.flask_app.route("/")(self.index)
        self.flask_app.route("/download", methods=["POST"])(self.download)
        self.flask_app.route("/health")(self.health)

    def index(self) -> str:
        """Main page"""
        return render_template("index.html")

    def create_download_response(self, file_path: str, filename: str) -> Response:
        """Create download response"""
        ascii_filename = create_ascii_filename(filename)

        response = send_file(
            file_path,
            as_attachment=True,
            download_name=ascii_filename,
            mimetype="application/octet-stream",
        )

        # Manually set Content-Disposition header (RFC 5987 compliant)
        # Override Flask's default header to support Japanese filenames properly
        response.headers["Content-Disposition"] = create_content_disposition_header(
            filename, ascii_filename
        )

        return response

    def download(self) -> Union[Response, Tuple[Response, int]]:
        """Download processing"""
        try:
            url = request.form.get("url")
            format_type = request.form.get("format")
            print(f"/download: [{format_type}] {url}", flush=True)

            if not url or not format_type:
                return jsonify({"error": "URLと形式を指定してください"}), 400

            # Execute download
            file_path, filename = download_video(url, format_type, self.download_dir)
            print(f'Save: "{file_path}"')

            # Create response
            return self.create_download_response(file_path, filename)
        except Exception as e:
            msg = str(e)
            print(msg)
            return jsonify({"error": msg}), 500

    def health(self) -> Response:
        """Health check"""
        return jsonify({"status": "ok"})

    def run(self) -> None:
        """Run the application"""
        self.flask_app.run(host=self.host, port=self.port, debug=False)


if __name__ == "__main__":
    app = App()
    app.run()
