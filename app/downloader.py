import os
import tempfile
import shutil
import subprocess

from video_utils import is_valid_video_url, clean_video_url
from file_utils import create_safe_filename, create_download_filename
from exceptions import VideoDownloadError, FileNotFoundError


def get_video_title(url):
    """Get video title"""
    title_cmd = ['yt-dlp', '--get-title', url]
    try:
        title_result = subprocess.run(title_cmd, capture_output=True, text=True, check=True)
        return title_result.stdout.strip()
    except subprocess.CalledProcessError:
        # Fallback when title acquisition fails (invalid URLs, deleted videos, etc.)
        return 'download'


def build_ytdlp_command(url, temp_dir, format_type):
    """Build yt-dlp command"""
    output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')

    if format_type == 'audio':
        return [
            'yt-dlp',
            '--format', 'bestaudio/best',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', '192',
            '--output', output_template,
            url
        ]
    else:
        return [
            'yt-dlp',
            '--format', 'bestvideo+bestaudio/best',
            '--merge-output-format', 'mp4',
            '--output', output_template,
            url
        ]


def execute_download(cmd):
    """Execute download"""
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise VideoDownloadError(f"ダウンロードエラー: {e.stderr.decode()}")


def find_downloaded_file(temp_dir):
    """Find downloaded file"""
    downloaded_files = []
    for file in os.listdir(temp_dir):
        if os.path.isfile(os.path.join(temp_dir, file)):
            downloaded_files.append(file)

    if not downloaded_files:
        raise FileNotFoundError("ダウンロードされたファイルが見つかりません")

    return downloaded_files[0]


def download_video(url, format_type='video', download_dir='/app/downloads'):
    """Download video"""
    if not is_valid_video_url(url):
        raise ValueError("有効な動画URL（YouTube/Twitter/TikTok）ではありません")

    # Remove unnecessary parameters from URL (to stabilize yt-dlp processing)
    clean_url = clean_video_url(url)

    # Use temporary directory (because yt-dlp generates unpredictable filenames)
    with tempfile.TemporaryDirectory() as temp_dir:
        title = get_video_title(clean_url)
        safe_title = create_safe_filename(title)

        cmd = build_ytdlp_command(clean_url, temp_dir, format_type)
        execute_download(cmd)

        downloaded_file = find_downloaded_file(temp_dir)
        source_file = os.path.join(temp_dir, downloaded_file)

        final_filename = create_download_filename(safe_title, format_type, downloaded_file)
        destination = os.path.join(download_dir, final_filename)

        # Copy file to final location (from temporary directory to persistent location)
        shutil.copy2(source_file, destination)

        return destination, final_filename

