import os
import tempfile
import shutil
import yt_dlp

from video_utils import is_valid_video_url, clean_video_url
from file_utils import create_safe_filename, create_download_filename
from exceptions import VideoDownloadError, FileNotFoundError


class ProgressHook:
    """Progress tracking for yt-dlp downloads"""

    def __init__(self):
        self.last_percent = -1

    def reset(self):
        """Reset progress tracking for new download"""
        self.last_percent = -1

    def __call__(self, d):
        """Progress hook for yt-dlp to show download progress"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                # Print progress every 1%
                if int(percent) != self.last_percent:
                    self.last_percent = int(percent)
                    print(f"Download progress: {int(percent)}%")
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
                # Print progress every 1%
                if int(percent) != self.last_percent:
                    self.last_percent = int(percent)
                    print(f"Download progress: {int(percent)}% (estimated)")
        elif d['status'] == 'finished':
            print(f"Download completed: {d['filename']}")

# Create progress hook instance
progress_hook = ProgressHook()


def get_video_title(url):
    """Get video title"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            return info_dict.get('title', 'download')
    except Exception:
        # Fallback when title acquisition fails (invalid URLs, deleted videos, etc.)
        return 'download'


def build_ytdlp_options(temp_dir, format_type):
    """Build yt-dlp options"""
    output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')

    base_opts = {
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [progress_hook],
    }

    if format_type == 'audio':
        base_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        base_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        })

    return base_opts


def execute_download(url, ydl_opts):
    """Execute download"""
    try:
        # Reset progress tracking for new download
        progress_hook.reset()
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        raise VideoDownloadError(f"ダウンロードエラー: {str(e)}")


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

        ydl_opts = build_ytdlp_options(temp_dir, format_type)
        execute_download(clean_url, ydl_opts)

        downloaded_file = find_downloaded_file(temp_dir)
        source_file = os.path.join(temp_dir, downloaded_file)

        final_filename = create_download_filename(safe_title, format_type, downloaded_file)
        destination = os.path.join(download_dir, final_filename)

        # Copy file to final location (from temporary directory to persistent location)
        shutil.copy2(source_file, destination)

        return destination, final_filename

