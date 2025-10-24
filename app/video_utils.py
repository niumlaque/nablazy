from typing import Iterable, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


YOUTUBE_BASE_DOMAINS = ("youtube.com",)
YOUTUBE_EXACT_HOSTS = ("youtu.be",)
TWITTER_BASE_DOMAINS = ("twitter.com", "x.com")
TIKTOK_BASE_DOMAINS = ("tiktok.com",)


def _normalize_hostname(hostname: Optional[str]) -> str:
    """Normalize hostname for comparison (lowercase, trim trailing dot)."""
    if not hostname:
        return ""
    return hostname.lower().rstrip(".")


def _hostname_matches(hostname: str, base_domains: Iterable[str], exact_hosts: Iterable[str] = ()) -> bool:
    """Return True when hostname matches allowed domains exactly or as subdomain."""
    if hostname in exact_hosts:
        return True
    for base in base_domains:
        if hostname == base or hostname.endswith(f".{base}"):
            return True
    return False


def is_valid_video_url(url: str) -> bool:
    """Check validity of video URL (YouTube/Twitter/TikTok)"""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    hostname = _normalize_hostname(parsed.hostname)

    # YouTube URLs
    if _hostname_matches(hostname, YOUTUBE_BASE_DOMAINS, YOUTUBE_EXACT_HOSTS):
        return True
    # Twitter/X URLs
    if _hostname_matches(hostname, TWITTER_BASE_DOMAINS):
        return True
    # TikTok URLs
    if _hostname_matches(hostname, TIKTOK_BASE_DOMAINS):
        return True
    return False


def clean_video_url(url: str) -> str:
    """Clean up video URL (keep only v= parameter for YouTube, remove tracking params for TikTok, return as-is for Twitter)"""
    parsed = urlparse(url)
    hostname = _normalize_hostname(parsed.hostname)

    # YouTube URLs - keep only v= parameter
    # Keep only v= parameter from YouTube URLs (other parameters may destabilize yt-dlp processing)
    if _hostname_matches(hostname, YOUTUBE_BASE_DOMAINS, YOUTUBE_EXACT_HOSTS):
        query_params = parse_qs(parsed.query)
        if "v" in query_params:
            clean_params = {"v": query_params["v"]}
            new_query = urlencode(clean_params, doseq=True)
            new_parsed = parsed._replace(query=new_query)
            return urlunparse(new_parsed)

    # TikTok URLs - remove tracking parameters
    if _hostname_matches(hostname, TIKTOK_BASE_DOMAINS):
        # Remove tracking parameters like is_copy_url, is_from_webapp
        new_parsed = parsed._replace(query="")
        return urlunparse(new_parsed)

    # Twitter/X URLs - return as-is
    return url
