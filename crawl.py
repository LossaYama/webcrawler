from urllib.parse import ParseResult, urlparse, urljoin
from bs4 import BeautifulSoup
from typing import TypedDict

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

def get_urls_from_html(html: str, base_url:str) -> list[str]:
    soup = BeautifulSoup(html, features="html.parser")
    urls = []
    anchors = soup.find_all('a')
    for anchor in anchors:
        urls.append(urljoin(base_url, anchor.get('href')))
    return urls

def get_images_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, features="html.parser")
    imgs = []
    images = soup.find_all('img')
    for image in images:
        imgs.append(urljoin(base_url, image.get('src')))
    return imgs


class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

def extract_page_data(html: str, page_url: str) -> PageData:
    return {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url)
    }