from urllib.parse import ParseResult, urlparse
from bs4 import BeautifulSoup

def normalize_url(url: str) -> str:
    parsed: ParseResult = urlparse(url)
    normal: str = (parsed.netloc + parsed.path).lower()
    if normal[-1] == '/':
        normal = normal[:-1]
    return normal

def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, features="html.parser")
    if soup.find('h1') != None:
        header = soup.find('h1')
    elif soup.find('h2') != None:
        header = soup.find('h2')
    else:
        return ""
    return header.get_text()

def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, features="html.parser")
    if soup.find('main') != None:
        paragraph = soup.find('main').find('p')
    elif soup.find('main') == None and soup.find('p') != None:
        paragraph = soup.find('p')
    else:
        return ""
    return paragraph.get_text()