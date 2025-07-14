import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def is_valid_video_url(url):
    """Check validity of video URL (YouTube/Twitter)"""
    parsed = urlparse(url)
    # YouTube URLs
    if (parsed.netloc in ['www.youtube.com', 'youtube.com', 'youtu.be'] or
            'youtube.com' in parsed.netloc):
        return True
    # Twitter/X URLs
    if (parsed.netloc in ['twitter.com', 'www.twitter.com', 'x.com', 'www.x.com'] or
            'twitter.com' in parsed.netloc or 'x.com' in parsed.netloc):
        return True
    return False


def clean_video_url(url):
    """Clean up video URL (keep only v= parameter for YouTube, return as-is for Twitter)"""
    parsed = urlparse(url)

    # YouTube URLs - keep only v= parameter
    # Keep only v= parameter from YouTube URLs (other parameters may destabilize yt-dlp processing)
    if (parsed.netloc in ['www.youtube.com', 'youtube.com', 'youtu.be'] or
            'youtube.com' in parsed.netloc):
        query_params = parse_qs(parsed.query)
        if 'v' in query_params:
            clean_params = {'v': query_params['v']}
            new_query = urlencode(clean_params, doseq=True)
            new_parsed = parsed._replace(query=new_query)
            return urlunparse(new_parsed)

    # Twitter/X URLs - return as-is
    return url


