import sys
from crawl import *
from json_report import write_json_report

async def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    elif len(sys.argv) > 4:
        print("too many arguments provided")
        sys.exit(1)
    else:
        print(f"starting crawl of: {sys.argv[1]}")

    data = await crawl_site_async(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    write_json_report(data)
    print(f"Pages crawled: {len(data.keys())}")


if __name__ == "__main__":
    asyncio.run(main())
