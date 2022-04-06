import os
import re
import urllib

import requests
from slugify import slugify

ICONFINDER_API_KEY = os.getenv("ICONFINDER_API_KEY")
if ICONFINDER_API_KEY is None:
    print("There is no API key for Iconfinder, this integration will not work")

HEADERS = {"Accept": "application/json", "Authorization": f"Bearer {ICONFINDER_API_KEY}"}

icon_id_re = re.compile(r"(?P<icon_id>\d+)\/(\w+)?$")


def download_icon(url, **kwargs):
    match = icon_id_re.search(url)
    icon_id = match.groupdict()["icon_id"]

    url = f"https://api.iconfinder.com/v4/icons/{icon_id}"
    response = requests.request("GET", url, headers=HEADERS)
    _download_just_icon(response)


def _download_just_icon(response):
    icon = response.json()
    icon_id = icon["icon_id"]
    [svg] = [_svg for _svg in icon["vector_sizes"][0]["formats"] if _svg["format"] == "svg"]
    tags = icon.get("tags", [])
    opener = urllib.request.build_opener()
    opener.addheaders = [("Authorization", HEADERS["Authorization"])]
    urllib.request.install_opener(opener)
    name = slugify(icon["iconset"]["name"])
    name_parts = [str(icon_id), name] + tags
    urllib.request.urlretrieve(svg["download_url"], f"{'-'.join(name_parts)}.svg")
