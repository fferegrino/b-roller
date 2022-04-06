import os
import re
from urllib.request import urlretrieve

import requests

urls_sizes = ["raw", "full", "regular", "small", "thumb"]


UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
if UNSPLASH_ACCESS_KEY is None:
    print("There is no API key for Unsplash, this integration will not work")


video_id_re = re.compile(r"(?P<video_id>[\w-]+)\/?$")


def download_unsplash_picture(url, **kwargs):
    match = video_id_re.search(url)
    video_id = match.group().strip("/")
    response = requests.get(
        f"https://api.unsplash.com/photos/{video_id}", headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    )
    json = response.json()

    tags = "-".join([tag["title"] for tag in json.get("tags", list()) if "title" in tag][:4])

    img_url = ""
    for url_type in urls_sizes:
        if url_type in json["urls"]:
            img_url = json["urls"][url_type]
            break

    urlretrieve(img_url, f"{video_id}-{tags}.jpg")
