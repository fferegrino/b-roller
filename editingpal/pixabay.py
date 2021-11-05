import os
from urllib.parse import urlparse
from urllib.request import urlretrieve

import requests

pixabay_videos = ["large", "medium", "small", "tiny"]

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")


def download_pixabay_video(url):
    parsed = urlparse(url)
    video_id = [abc for abc in parsed.path.split("/") if abc][-1][3:]
    result = requests.get(f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&id={video_id}")
    values = result.json()
    [hit] = values["hits"]
    tags = "-".join([tag.strip() for tag in hit["tags"].split(",")])
    values = hit["videos"]
    video_resource = dict()
    for size in pixabay_videos:
        if size in values and values[size]["url"]:
            video_resource = values[size]
            break
    video_url = urlparse(video_resource["url"])
    if video_url.query:
        download = "&download=1"
    else:
        download = "?download=1"
    file_name = f"{tags}-{video_resource['width']}x{video_resource['height']}-{video_id}.mp4"
    urlretrieve(video_resource["url"] + download, file_name)
