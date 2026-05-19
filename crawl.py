from urllib.parse import ParseResult, urlparse, urljoin
from bs4 import BeautifulSoup
from typing import TypedDict
import asyncio
import aiohttp


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


class AsyncCrawler:
    def __init__(self, base_url: str, max_concurrency, max_pages):
        self.base_url = base_url
        self.base_domain = urlparse(self.base_url).netloc
        self.page_data = {}
        self.visited = set()
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session = None
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks = set()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url):
        if self.should_stop is True:
            return False
        async with self.lock:
            if normalized_url in self.visited:
                return False
            self.visited.add(normalized_url)
            return True
            
    async def fetch(self, url):
        async with self.session.get(url,headers={"User-Agent": "BootCrawler/1.0"}) as resp:
            return await resp
    
    async def get_html(self, url: str) -> str:
        async with self.session.get(url) as webpage:
            if webpage.status >= 400:
                raise Exception("Error: status code 400+")
            if "text/html" not in webpage.headers['content-type']:
                raise Exception("Error: content type is not html text")       
            return await webpage.text()
        
    async def crawl_page(self, current_url):
        if urlparse(self.base_url).netloc != urlparse(current_url).netloc:
            return
        if await self.add_page_visit(normalize_url(current_url)) is False:
            return
        if self.should_stop is True:
            return
       
        try:
            async with self.semaphore:
                html = await self.get_html(current_url)
            if html != None:
                async with self.lock:
                    self.page_data[normalize_url(current_url)] = extract_page_data(html, current_url)
                    if len(self.page_data) >= self.max_pages:
                        self.should_stop = True
                        print("Reached maximum number of pages to crawl.")
                        for task in self.all_tasks:
                            if task is not asyncio.current_task():
                                task.cancel()
                response_urls = get_urls_from_html(html, current_url)
                for url in response_urls:
                    task = asyncio.create_task(self.crawl_page(url))
                    self.all_tasks.add(task)
                    task.add_done_callback(self.all_tasks.discard)
        except Exception as e:
            print(f"{normalize_url(current_url)}: {e}")
        
    
    async def crawl(self):
        await self.crawl_page(self.base_url)
        while self.all_tasks:
            current = list(self.all_tasks)
            await asyncio.gather(*current, return_exceptions=True)
        return self.page_data

async def crawl_site_async(base_url, max_concurrency, max_pages):
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
        return await crawler.crawl()