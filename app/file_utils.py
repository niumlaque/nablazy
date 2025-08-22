import os
import re
from urllib.parse import quote

# Constants for filename limits
DEFAULT_MAX_FILENAME_BYTES = 200
DEFAULT_MAX_FILENAME_CHARS = 100


def create_safe_filename(
    title, max_bytes=DEFAULT_MAX_FILENAME_BYTES, max_chars=DEFAULT_MAX_FILENAME_CHARS
):
    """Convert to safe filename"""
    # Remove characters forbidden by filesystems (for Windows/Linux/macOS compatibility)
    safe_title = re.sub(r'[<>:"/\\|?*]', "", title)
    safe_title = safe_title.strip()

    # Check both byte length and character count to handle filesystem limitations
    # (some filesystems have byte limits, others have character limits)
    if len(safe_title.encode("utf-8")) > max_bytes:
        safe_title = safe_title[:max_chars]

    return safe_title


def create_download_filename(safe_title, format_type, original_filename=None):
    """Create filename for download"""
    if format_type == "audio":
        return f"{safe_title}.mp3"
    else:
        if original_filename:
            _, ext = os.path.splitext(original_filename)
            extension = ext.lstrip(".") if ext else "mp4"
        else:
            extension = "mp4"
        return f"{safe_title}.{extension}"


def create_ascii_filename(filename):
    """Create ASCII safe filename"""
    name_part, ext_part = os.path.splitext(filename)
    ascii_name = re.sub(r"[^\x00-\x7F]", "_", name_part)
    return ascii_name + ext_part


def create_content_disposition_header(filename, ascii_filename):
    """Create content disposition header"""
    # Manual Content-Disposition header creation is needed because:
    # 1. Japanese video titles cause filename encoding issues in browsers
    # 2. Flask's send_file() download_name parameter only supports ASCII characters
    # 3. RFC 5987 compliance requires both ASCII fallback and UTF-8 encoded versions:
    #    - filename="ascii_safe.mp4" (for old browsers)
    #    - filename*=UTF-8'''encoded_filename (for modern browsers with unicode support)
    # This ensures proper download filename display across all browsers
    encoded_filename = quote(filename.encode("utf-8"))
    return f"attachment; filename=\"{ascii_filename}\"; filename*=UTF-8'''{encoded_filename}"
