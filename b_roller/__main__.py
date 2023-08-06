import json
import logging
from pathlib import Path
from typing import Optional

import typer

from b_roller.credits import add_credit_url
from b_roller.iconfinder import download_icon
from b_roller.pexels import download_pexels_video
from b_roller.youtube import download_video, get_video_id, to_hh_mm_ss

app = typer.Typer(add_completion=False)


def get_secrets():
    secrets_files = [Path(Path().home(), ".b-roller.secrets.json"), Path(".b-roller.secrets.json")]
    for secrets_file in secrets_files:
        if secrets_file.exists():
            with open(secrets_file, "r") as read:
                return json.load(read)
    else:
        return {}


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
    audio: bool = typer.Option(False, "--audio", help="Download only the audio"),
    video: bool = typer.Option(False, "--video", help="Download only the video"),
    no_credits: bool = typer.Option(False, "--no-credits", help="Do not add credits"),
):
    """
    Download content from YouTube
    """
    if video_id := get_video_id(url):
        download = "both"
        if audio:
            download = "audio"
        elif video:
            download = "video"

        video = download_video(video_id, start_time=to_hh_mm_ss(start), end_time=to_hh_mm_ss(end), download=download)
        if not no_credits:
            add_credit_url(video.watch_url, video.title)
    else:
        print(f'"{url}" does not look like a YouTube video')


@app.command()
@app.command("px")
def pexels(
    url: str = typer.Argument(..., help="The url for a Pexels video"),
    no_credits: bool = typer.Option(False, "--no-credits", help="Do not add credits"),
):
    """
    Download content from Pexels, remember that you need an API key
    """
    if secrets := get_secrets():
        if api_key := secrets.get("PEXELS_API_KEY"):
            title, url = download_pexels_video(url, api_key)
            if not no_credits:
                add_credit_url(url, title)


@app.command()
@app.command("if")
def iconfinder(
    url: str = typer.Argument(..., help="The url for a Pexels video"),
    no_credits: bool = typer.Option(False, "--no-credits", help="Do not add credits"),
):
    """
    Download content from Iconfinder, remember that you need an API key
    """
    if secrets := get_secrets():
        if api_key := secrets.get("ICONFINDER_API_KEY"):
            title, url = download_icon(url, api_key)
            if not no_credits:
                add_credit_url(url, title)


@app.command()
def clear_cache():
    """
    Clear the cache
    """
    from b_roller.settings import cache

    if cache.exists():
        for file in cache.iterdir():
            file.unlink()
    else:
        cache.mkdir()


@app.command()
def init():
    pass


@app.callback()
def callback(verbose: int = typer.Option(0, "--verbose", "-v", count=True, help="Increase verbosity")):
    log_level = logging.WARNING
    if verbose > 1:
        log_level = logging.DEBUG
    elif verbose > 0:
        log_level = logging.INFO

    logger = logging.getLogger("b_roller")
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    logger.addHandler(handler)

    from b_roller.settings import cache

    cache.mkdir(exist_ok=True)
    logger.debug(f"Cache: {cache}")


if __name__ == "__main__":
    print(get_secrets())
    # app()
