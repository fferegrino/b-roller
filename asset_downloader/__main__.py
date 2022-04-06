import argparse
from urllib.parse import urlparse

import typer

from asset_downloader.giphy import download_giphy
from asset_downloader.iconfinder import download_icon
from asset_downloader.pexels import download_pexels_video
from asset_downloader.pixabay import download_pixabay_video
from asset_downloader.unsplash import download_unsplash_picture
from asset_downloader.youtube import download_youtube_audio, download_youtube_video

app = typer.Typer(add_completion=False)


@app.command()
def video(url: str):
    download_youtube_video(url)


@app.command()
def audio(url: str):
    download_youtube_audio(url)


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
    ("youtube.com", ""): download_youtube_video,
    ("youtube.com", "video"): download_youtube_video,
    ("youtube.com", "audio"): download_youtube_audio,
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
