from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.request import urlretrieve

import requests

pixabay_videos = ["large", "medium", "small", "tiny"]


@dataclass
class PexelsUrl:
    kind: str
    name: str
    identifier: str


def parse_pexels_video_url(url: str) -> PexelsUrl:
    parsed = urlparse(url)
    kind, _, path = parsed.path.strip("/").partition("/")
    name, _, identifier = path.rpartition("-")

    return PexelsUrl(kind, name, identifier)


def make_title_from_slug(slug: str) -> str:
    return " ".join([part.title() for part in slug.split("-")])


def download_pexels_video(url, api_key):
    parsed = parse_pexels_video_url(url)
    if parsed.kind != "video":
        raise ValueError(f"No method implemented to download files of type {parsed.kind} yet")

    result = requests.get(
        f"https://api.pexels.com/videos/videos/{parsed.identifier}", headers={"Authorization": api_key}
    )

    values = result.json()
    video_files = values["video_files"]
    video_resource = sorted(video_files, key=lambda vid: (vid.get("width") or 0) * (vid.get("height") or 0))[-1]
    video_url = urlparse(video_resource["link"])
    if video_url.query:
        download = "&download=1"
    else:
        download = "?download=1"
    file_name = f"{parsed.name}-{video_resource['width']}x{video_resource['height']}-{parsed.identifier}.mp4"
    urlretrieve(video_resource["link"] + download, file_name)

    user = values["user"]["name"]
    title = make_title_from_slug(parsed.name)
    return f"{title} by {user}", url
