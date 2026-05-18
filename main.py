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

    url = 'https://learnwebscraping.dev/practice/ecommerce/products/ashenfang-longsword-fan-1001/'
    print(get_html(url))


if __name__ == "__main__":
    main()
