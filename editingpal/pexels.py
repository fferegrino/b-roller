import os
import re
from urllib.parse import urlparse
from urllib.request import urlretrieve

import requests

pixabay_videos = ["large", "medium", "small", "tiny"]

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
if PEXELS_API_KEY is None:
    print("There is no API key for Pexels, this integration will not work")

video_id_re = re.compile(r"(?P<video_id>\d+)\/?$")

# https://api.pexels.com/videos/videos/:id


def download_pexels_video(url, **kwargs):
    match = video_id_re.search(url)
    video_id = match.group().strip("/")
    result = requests.get(f"https://api.pexels.com/videos/videos/{video_id}", headers={"Authorization": PEXELS_API_KEY})
    values = result.json()
    video_files = values["video_files"]
    video_resource = sorted(video_files, key=lambda vid: (vid.get("width") or 0) * (vid.get("height") or 0))[-1]
    video_url = urlparse(video_resource["link"])
    if video_url.query:
        download = "&download=1"
    else:
        download = "?download=1"
    file_name = f"{values['id']}-{video_resource['width']}x{video_resource['height']}-{video_id}.mp4"
    urlretrieve(video_resource["link"] + download, file_name)
