from typing import Any, Dict, List, Optional, Tuple
import os
import tempfile
import shutil
import yt_dlp

from video_utils import is_valid_video_url, clean_video_url
from file_utils import create_safe_filename, create_download_filename
from exceptions import VideoDownloadError, FileNotFoundError
from progress import progress_stream


class ProgressHook:
    """Progress tracking for yt-dlp downloads"""

    last_percent: int

    def __init__(self) -> None:
        self.last_percent = -1
        self.session_id: Optional[str] = None

    def reset(self) -> None:
        """Reset progress tracking for new download"""
        self.last_percent = -1

    def attach_session(self, session_id: Optional[str]) -> None:
        """Bind the hook to a session for SSE publishing"""
        self.session_id = session_id

    def _emit(self, message: str) -> None:
        """Publish progress to console and SSE"""
        print(message, flush=True)
        if self.session_id:
            progress_stream.publish(self.session_id, message)

    def __call__(self, d: Dict[str, Any]) -> None:
        """Progress hook for yt-dlp to show download progress"""
        if d["status"] == "downloading":
            if "total_bytes" in d and d["total_bytes"]:
                percent = d["downloaded_bytes"] / d["total_bytes"] * 100
                # Print progress every 1%
                if int(percent) != self.last_percent:
                    self.last_percent = int(percent)
                    self._emit(f"Download progress: {int(percent)}%")
            elif "total_bytes_estimate" in d and d["total_bytes_estimate"]:
                percent = d["downloaded_bytes"] / d["total_bytes_estimate"] * 100
                # Print progress every 1%
                if int(percent) != self.last_percent:
                    self.last_percent = int(percent)
                    self._emit(f"Download progress: {int(percent)}% (estimated)")
        elif d["status"] == "finished":
            self._emit("Download completed")


class PostProcessorHook:
    """Postprocessing tracking for yt-dlp downloads"""

    def __init__(self) -> None:
        self.session_id: Optional[str] = None

    def attach_session(self, session_id: Optional[str]) -> None:
        """Bind the hook to a session for SSE publishing"""
        self.session_id = session_id

    def _emit(self, message: str) -> None:
        """Publish postprocessing status to console and SSE"""
        print(message, flush=True)
        if self.session_id:
            progress_stream.publish(self.session_id, message)

    def __call__(self, d: Dict[str, Any]) -> None:
        """Postprocessor hook callback"""
        postprocessor = d.get("postprocessor")
        status = d.get("status")

        if postprocessor not in ["FFmpegExtractAudio", "ExtractAudio"]:
            print(f"Unexpected postprocessor: {postprocessor}")
            return

        if status == "started":
            self._emit("Audio conversion started")
        elif status == "processing":
            self._emit("Audio conversion in progress")
        elif status == "finished":
            self._emit("Audio conversion completed")


class Downloader:
    """Video downloader class"""

    progress_hook: ProgressHook

    def __init__(self) -> None:
        self.progress_hook = ProgressHook()
        self.postprocessor_hook = PostProcessorHook()

    def get_video_title(self, url: str) -> str:
        """Get video title"""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                if isinstance(info_dict, dict):
                    return str(info_dict.get("title", "download"))
                else:
                    return "download"
        except Exception:
            # Fallback when title acquisition fails (invalid URLs, deleted videos, etc.)
            return "download"

    def build_ytdlp_options(self, temp_dir: str, format_type: str) -> Dict[str, Any]:
        """Build yt-dlp options"""
        output_template = os.path.join(temp_dir, "%(title)s.%(ext)s")

        base_opts = {
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [self.progress_hook],
        }

        if format_type == "audio":
            base_opts.update(
                {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                    "postprocessor_hooks": [self.postprocessor_hook],
                }
            )
        else:
            base_opts.update(
                {
                    "format": "bestvideo+bestaudio/best",
                    "merge_output_format": "mp4",
                }
            )

        return base_opts

    def execute_download(
        self, url: str, ydl_opts: Dict[str, Any], session_id: Optional[str]
    ) -> None:
        """Execute download"""
        try:
            # Reset progress tracking for new download
            self.progress_hook.reset()
            self.progress_hook.attach_session(session_id)
            self.postprocessor_hook.attach_session(session_id)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            raise VideoDownloadError(f"ダウンロードエラー: {str(e)}")

    def find_downloaded_file(self, temp_dir: str) -> str:
        """Find downloaded file"""
        downloaded_files: List[str] = []
        for file in os.listdir(temp_dir):
            if os.path.isfile(os.path.join(temp_dir, file)):
                downloaded_files.append(file)

        if not downloaded_files:
            raise FileNotFoundError("ダウンロードされたファイルが見つかりません")

        return downloaded_files[0]

    def download_video(
        self,
        url: str,
        format_type: str = "video",
        download_dir: str = "/app/downloads",
        session_id: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Download video"""
        try:
            if not is_valid_video_url(url):
                raise ValueError("有効な動画URL（YouTube/Twitter/TikTok）ではありません")

            # Remove unnecessary parameters from URL (to stabilize yt-dlp processing)
            clean_url = clean_video_url(url)

            # Use temporary directory (because yt-dlp generates unpredictable filenames)
            with tempfile.TemporaryDirectory() as temp_dir:
                title = self.get_video_title(clean_url)
                safe_title = create_safe_filename(title)

                ydl_opts = self.build_ytdlp_options(temp_dir, format_type)
                self.execute_download(clean_url, ydl_opts, session_id)

                downloaded_file = self.find_downloaded_file(temp_dir)
                source_file = os.path.join(temp_dir, downloaded_file)

                final_filename = create_download_filename(
                    safe_title, format_type, downloaded_file
                )
                destination = os.path.join(download_dir, final_filename)

                # Move file from temporary directory to persistent location to avoid extra copy
                shutil.move(source_file, destination)

                return destination, final_filename
        finally:
            if session_id:
                progress_stream.close(session_id)


# Backward compatibility function
def download_video(
    url: str,
    format_type: str = "video",
    download_dir: str = "/app/downloads",
    session_id: Optional[str] = None,
) -> Tuple[str, str]:
    """Download video (backward compatibility function)"""
    downloader = Downloader()
    return downloader.download_video(url, format_type, download_dir, session_id)
