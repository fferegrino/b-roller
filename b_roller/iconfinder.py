import urllib
from urllib.parse import urlparse

import requests
from slugify import slugify


def parse_url(url):
    parts = urlparse(url)
    [*_, type_, identifier, slug] = parts.path.split("/")
    return type_, identifier, slug


def download_icon(url, iconfinder_api_key, **kwargs):
    type_, icon_id, slug = parse_url(url)
    url = f"https://api.iconfinder.com/v4/icons/{icon_id}"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {iconfinder_api_key}"}
    response = requests.request("GET", url, headers=headers)
    icon_name = _download_just_icon(response, headers)
    return icon_name, url


def _download_just_icon(response, headers):
    icon = response.json()
    icon_id = icon["icon_id"]
    [svg] = [_svg for _svg in icon["vector_sizes"][0]["formats"] if _svg["format"] == "svg"]
    tags = icon.get("tags", [])
    opener = urllib.request.build_opener()
    opener.addheaders = [("Authorization", headers["Authorization"])]
    urllib.request.install_opener(opener)
    name = slugify(icon["iconset"]["name"])
    name_parts = [str(icon_id), name] + tags
    urllib.request.urlretrieve(svg["download_url"], f"{'-'.join(name_parts)}.svg")

    return icon["iconset"]["name"]
