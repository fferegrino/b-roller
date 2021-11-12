from urllib.parse import urlparse

import typer

from editingpal.giphy import download_giphy
from editingpal.pexels import download_pexels_video
from editingpal.pixabay import download_pixabay_video
from editingpal.unsplash import download_unsplash_picture
from editingpal.youtube import download_youtube_audio, download_youtube_video

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
}


@app.command()
def cli():
    command = ""
    while True:
        print("Enter an url or q to exit")
        command = input().strip()
        if command == "q":
            break

        [str_url, *extras] = command.split()
        extra = "".join(extras)
        url = urlparse(str_url)

        netloc = url.netloc[4:] if url.netloc.startswith("www.") else url.netloc

        cli_fns[(netloc, extra)](str_url)
        print(f"the content has been downloaded from {netloc}")
    print("goodbye")


if __name__ == "__main__":
    app()
