import sys
from crawl import *

def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    else:
        print(f"starting crawl of: {sys.argv[1]}")

    data = crawl_page(sys.argv[1])
    print(f"Pages crawled: {len(data.keys())}")
    for page in data.values():
        print(f" - {page['url']}: {page['heading']}\n{page['first_paragraph']}")

if __name__ == "__main__":
    main()
