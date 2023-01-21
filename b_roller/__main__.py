from typing import Optional

import typer

from b_roller.credits import add_credit_url
from b_roller.youtube import download_video, get_video_id, to_hh_mm_ss

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
def init():
    pass


if __name__ == "__main__":
    app()
