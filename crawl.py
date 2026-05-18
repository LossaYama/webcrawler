from urllib.parse import ParseResult, urlparse

def normalize_url(url: str) -> str:
    parsed: ParseResult = urlparse(url)
    normal: str = (parsed.netloc + parsed.path).lower()
    if normal[-1] == '/':
        normal = normal[:-1]
    return normal