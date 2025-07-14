"""Application exception classes"""


class DownloadError(Exception):
    """Download related errors"""
    pass


class VideoTitleError(DownloadError):
    """Video title acquisition error"""
    pass


class VideoDownloadError(DownloadError):
    """Video download execution error"""
    pass


class FileNotFoundError(DownloadError):
    """Downloaded file not found error"""
    pass

