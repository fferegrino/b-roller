import logging
from typing import Optional
from urllib.parse import parse_qs, urlparse

import ffmpeg
from pytube import YouTube
from pytube.streams import Stream
from slugify import slugify

video_itags = [137, 136, 135, 134, 133, 160]
audio_itags = [140, 139]


def to_hh_mm_ss(time):
    if time is None:
        return None
    try:
        [*possibly_hours, remaining_minutes, remaining_seconds] = [int(part) for part in time.split(":")]
        if not possibly_hours:
            hours = 0
        else:
            hours = possibly_hours[0]
    except ValueError:
        seconds = int(time)
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        hours = minutes // 60
        remaining_minutes = minutes % 60
    return f"{hours:02}:{remaining_minutes:02}:{remaining_seconds:02}"


def get_video_id(url):
    parts = urlparse(url)
    if parts.netloc in {"www.youtube.com", "youtube.com"}:
        if parts.path == "/watch":
            return parse_qs(parts.query)["v"][0]
    elif parts.netloc == "youtu.be":
        return parts.path.lstrip("/")
    else:
        return None


def get_streams(video: YouTube, kind: str) -> Stream:
    args = {}
    if kind == "video":
        args["only_video"] = True
        mime_type = "video/mp4"
        streams = [stream for stream in video.streams.filter(**args) if stream.mime_type == mime_type]
        sorted_streams = sorted(
            streams, key=lambda stream: 1000 if stream.itag not in video_itags else video_itags.index(stream.itag)
        )
    elif kind == "audio":
        args["only_audio"] = True
        mime_type = "audio/mp4"
        streams = [stream for stream in video.streams.filter(**args) if stream.mime_type == mime_type]
        sorted_streams = sorted(
            streams, key=lambda stream: 1000 if stream.itag not in audio_itags else audio_itags.index(stream.itag)
        )

    return sorted_streams[0]


def download_video(video_id: str, start_time: Optional[str] = None, end_time: Optional[str] = None) -> YouTube:
    yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    name_slug = slugify(yt.title)

    original_name = f"{name_slug}__{video_id}"
    audio_file = f"{original_name}_audio.mp4"
    video_file = f"{original_name}_video.mp4"
    audio = get_streams(yt, "audio")
    video = get_streams(yt, "video")

    audio.download(filename=audio_file)
    video.download(filename=video_file)

    try:
        ffmpeg_processing(audio_file, video_file, original_name, end_time, start_time)
    except FileNotFoundError:
        logging.warning("No ffmpeg is not available")

    return yt


def ffmpeg_processing(
    audio_file: str,
    video_file: str,
    original_name: str,
    end_time: Optional[str] = None,
    start_time: Optional[str] = None,
) -> None:

    ffmpeg_arguments = {}
    if start_time:
        ffmpeg_arguments["ss"] = start_time
    if end_time:
        ffmpeg_arguments["to"] = end_time
    input_video = ffmpeg.input(video_file, **ffmpeg_arguments)
    input_audio = ffmpeg.input(audio_file, **ffmpeg_arguments)
    ffmpeg.concat(input_video, input_audio, v=1, a=1).output(
        f"./{original_name}.mp4",
    ).run(quiet=True, overwrite_output=True)
