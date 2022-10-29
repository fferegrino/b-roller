from pathlib import Path
from typing import Optional

import typer

from b_roller.youtube import download_video, get_video_id, to_hh_mm_ss

app = typer.Typer(add_completion=False)

credits_file = Path("credits.tsv")


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
        video = download_video(video_id, start_time=to_hh_mm_ss(start), end_time=to_hh_mm_ss(end))
        if credits_file.exists():
            with open(credits_file, "a") as append:
                append.write(f"{video.title}\t{video.watch_url}")
    else:
        print(f'"{url}" does not look like a YouTube video')


@app.command()
def init():
    if credits_file.exists():
        pass
    else:
        credits_file.touch()


if __name__ == "__main__":
    app()
