import os
import time
import requests
import unittest
from urllib.parse import quote, unquote


class TestIntegration(unittest.TestCase):
    """Integration tests for application in container"""

    BASE_URL = "http://localhost:8080"
    DOWNLOAD_DIR = "./downloads"

    @classmethod
    def setUpClass(cls):
        """Check application is running before test class starts"""
        # Check application startup with health check
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(f"{cls.BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    print("Application is ready")
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)

        raise Exception("Application did not start within expected time")

    def test_should_download_video_format_with_correct_title_and_extension(self):
        """Test 1: Download in video format with correct title and extension"""
        url = "https://www.youtube.com/watch?v=bjmBJ1Fl0cs"

        # Send download request
        response = requests.post(
            f"{self.BASE_URL}/download",
            data={"url": url, "format": "video"},
            timeout=120
        )

        # Confirm response is successful
        self.assertEqual(response.status_code, 200)

        # Extract filename from Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition', '')
        self.assertIn('attachment', content_disposition)

        filename = self._extract_filename_from_content_disposition(content_disposition)

        # Confirm that title contains "著作権フリーサンプル動画 1"
        clean_filename = filename.strip("'\" ")
        expected_title = "著作権フリーサンプル動画 1"

        # Confirm that filename contains expected title
        self.assertIn(
            expected_title,
            clean_filename,
            f"Filename '{clean_filename}' does not contain expected title '{expected_title}'"
        )

        # Confirm that appropriate extension for video format is assigned
        self.assertTrue(
            clean_filename.endswith(('.mp4', '.webm', '.mkv')),
            f"Filename '{clean_filename}' does not have expected video extension"
        )

        # Confirm that response body contains file data
        self.assertGreater(len(response.content), 0)

        print(f"Video test passed. Downloaded: {clean_filename}")

    def test_should_download_audio_format_with_correct_title_and_mp3_extension(self):
        """Test 2: Download in audio format with correct title and mp3 extension"""
        url = "https://www.youtube.com/watch?v=bjmBJ1Fl0cs"

        # Send download request
        response = requests.post(
            f"{self.BASE_URL}/download",
            data={"url": url, "format": "audio"},
            timeout=120
        )

        # Confirm response is successful
        self.assertEqual(response.status_code, 200)

        # Extract filename from Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition', '')
        self.assertIn('attachment', content_disposition)

        filename = self._extract_filename_from_content_disposition(content_disposition)

        # Confirm that title contains "著作権フリーサンプル動画 1"
        clean_filename = filename.strip("'\" ")
        expected_title = "著作権フリーサンプル動画 1"

        # Confirm that filename contains expected title
        self.assertIn(
            expected_title,
            clean_filename,
            f"Filename '{clean_filename}' does not contain expected title '{expected_title}'"
        )

        # Confirm that .mp3 extension is assigned
        self.assertTrue(
            clean_filename.endswith('.mp3'),
            f"Filename '{clean_filename}' does not have .mp3 extension"
        )

        # Confirm that response body contains file data
        self.assertGreater(len(response.content), 0)

        print(f"Audio test passed. Downloaded: {clean_filename}")

    def test_should_download_twitter_video_with_correct_extension(self):
        """Test 3: Download Twitter video in video format with appropriate extension"""
        url = "https://x.com/trorez/status/1280440336855138304?s=46&t=ELSr1I78F3BnPuHrFtlWPQ"

        # Send download request
        response = requests.post(
            f"{self.BASE_URL}/download",
            data={"url": url, "format": "video"},
            timeout=120
        )

        # Confirm response is successful
        self.assertEqual(response.status_code, 200)

        # Extract filename from Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition', '')
        self.assertIn('attachment', content_disposition)

        filename = self._extract_filename_from_content_disposition(content_disposition)

        # Confirm that filename is not empty
        clean_filename = filename.strip("'\" ")
        self.assertNotEqual(clean_filename, "")
        self.assertNotEqual(clean_filename, "unknown_filename")

        # Confirm that appropriate extension for video format is assigned
        self.assertTrue(
            clean_filename.endswith(('.mp4', '.webm', '.mkv')),
            f"Filename '{clean_filename}' does not have expected video extension"
        )

        # Confirm that response body contains file data
        self.assertGreater(len(response.content), 0)

        print(f"Twitter video test passed. Downloaded: {clean_filename}")

    def _extract_filename_from_content_disposition(self, content_disposition):
        """Extract filename from Content-Disposition header"""

        # Prioritize extracting UTF-8 encoded filename
        if "filename*=UTF-8'''" in content_disposition:
            parts = content_disposition.split("filename*=UTF-8'''")
            if len(parts) > 1:
                encoded_filename = parts[1].strip()
                decoded_filename = unquote(encoded_filename)
                return decoded_filename

        # Fallback: use regular filename attribute
        if 'filename="' in content_disposition:
            parts = content_disposition.split('filename="')
            if len(parts) > 1:
                filename_part = parts[1]
                if '"' in filename_part:
                    fallback_filename = filename_part.split('"')[0]
                    return fallback_filename

        return "unknown_filename"

    def test_health_check(self):
        """Confirm that health check endpoint works correctly"""
        response = requests.get(f"{self.BASE_URL}/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})

    def test_invalid_url_returns_error(self):
        """Confirm that error is returned for invalid URL"""
        response = requests.post(
            f"{self.BASE_URL}/download",
            data={"url": "https://invalid-url.com", "format": "video"},
            timeout=30
        )
        self.assertEqual(response.status_code, 500)
        error_data = response.json()
        self.assertIn('error', error_data)


if __name__ == '__main__':
    unittest.main(verbosity=2)

