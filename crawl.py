from urllib.parse import ParseResult, urlparse, urljoin
from bs4 import BeautifulSoup
from typing import TypedDict
import requests


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

def get_html(url: str) -> str:
    webpage = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
    if webpage.status_code >= 400:
        raise Exception("Error: request status code 400+")
    if "text/html" not in webpage.headers['content-type']:
        raise Exception("Error: content type is not html text")       
    return webpage.text

def crawl_page(base_url, current_url=None, page_data=None):
    if current_url == None:
        page_data = {}
        current_url = base_url
    if urlparse(base_url).netloc != urlparse(current_url).netloc:
        return page_data
    
    normal_current = normalize_url(current_url)
    if normal_current in page_data.keys():
        return page_data
    
    try:
        html = get_html(current_url)
        page_data[normal_current] = extract_page_data(html, current_url)
        response_urls = get_urls_from_html(html, current_url)
        for url in response_urls:
            crawl_page(base_url, url, page_data)
    except Exception as e:
        print(f"{normal_current}: {e}")
    
    
    return page_data
    