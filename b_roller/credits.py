import csv
from pathlib import Path

credits_file = Path("credits.csv")


def get_urls() -> set:
    if credits_file.exists():
        with open(credits_file, "r") as read:
            csv_reader = csv.reader(read)
            return {row[1] for row in csv_reader}
    else:
        return set()


def add_credit_url(url: str, title: str) -> None:
    urls = get_urls()
    if url not in urls:
        with open(credits_file, "a") as write:
            csv_writer = csv.writer(write)
            csv_writer.writerow([title, url])
