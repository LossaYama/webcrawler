import json

def write_json_report(page_data, filename="report.json"):
    pages = sorted(page_data.values(), key = lambda p: p['url'])
    with open(filename, "w", encoding="utf-8") as report:
        json.dump(pages, report, indent=2)