import os

import requests

GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

API_TEMPLATE = f"https://api.giphy.com/v1/gifs/{{}}?api_key={GIPHY_API_KEY}"
DEFAULT_TEMPLATE = "https://media.giphy.com/media/{}/source.gif"


def download_giphy(url):
    gif_name, _, gif_id = url.split("/")[-1].rpartition("-")

    if GIPHY_API_KEY:
        gif_info = requests.get(API_TEMPLATE.format(gif_id)).json()
        for field in ["hd", "original"]:
            if entry := gif_info["data"]["images"].get(field):
                url = entry["mp4"]
                break
        extension = "mp4"
    else:
        url = DEFAULT_TEMPLATE.format(gif_id)
        extension = "gif"

    with open(f"{gif_name}-{gif_id}.{extension}", "wb") as wb:
        wb.write(requests.get(url).content)