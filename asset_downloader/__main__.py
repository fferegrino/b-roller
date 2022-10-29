import argparse
from typing import Optional
from urllib.parse import urlparse

import typer

from asset_downloader.giphy import download_giphy
from asset_downloader.iconfinder import download_icon
from asset_downloader.pexels import download_pexels_video
from asset_downloader.pixabay import download_pixabay_video
from asset_downloader.unsplash import download_unsplash_picture
from asset_downloader.youtube import download_video, get_video_id, to_hh_mm_ss

app = typer.Typer(add_completion=False)


@app.command()
@app.command("yt")
def youtube(
    url: str = typer.Argument(..., help="A video id or a YouTube short/long url"),
    start: Optional[str] = typer.Argument(
        default=None, help="The desired start of the video in seconds or the format 00:00:00"
    ),
    end: Optional[str] = typer.Argument(
        default=None, help="The desired end of the video in seconds or the format 00:00:00"
    ),
):
    """
    Download content from YouTube
    """
    if video_id := get_video_id(url):
        download_video(video_id, start_time=to_hh_mm_ss(start), end_time=to_hh_mm_ss(end))
    else:
        print(f'"{url}" does not look like a YouTube video')


@app.command()
def pixabay(url: str):
    download_pixabay_video(url)


@app.command()
def giphy(url: str):
    download_giphy(url)


@app.command()
def unsplash(url: str):
    download_unsplash_picture(url)


cli_fns = {
    # ("youtube.com", ""): download_youtube_video,
    # ("youtube.com", "video"): download_youtube_video,
    # ("youtube.com", "audio"): download_youtube_audio,
    ("pixabay.com", ""): download_pixabay_video,
    ("giphy.com", ""): download_giphy,
    ("pexels.com", ""): download_pexels_video,
    ("unsplash.com", ""): download_unsplash_picture,
    ("iconfinder.com", ""): download_icon,
}


parser = argparse.ArgumentParser(description="Process some integers.")

parser.add_argument("url", type=str)
parser.add_argument("-k", "--kind", type=str, default="", required=False)
parser.add_argument("-s", "--start", type=str, default=None, required=False)
parser.add_argument("-e", "--end", type=str, default=None, required=False)


@app.command()
def cli():
    command = ""
    while True:
        print("Enter an url or q to exit")
        command = input().strip()
        if command == "q":
            break

        args = command.split()
        parsed_args = parser.parse_args(args).__dict__

        url = urlparse(parsed_args.pop("url"))
        netloc = url.netloc[4:] if url.netloc.startswith("www.") else url.netloc

        download_fn = cli_fns[(netloc, parsed_args.pop("kind"))]
        download_fn(url.geturl(), **parsed_args)
        print(f"the content has been downloaded from {netloc}")
    print("goodbye")


if __name__ == "__main__":
    app()
