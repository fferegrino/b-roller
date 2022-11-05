import logging
from pathlib import Path
from typing import Optional, Union
from urllib.parse import parse_qs, urlparse

import ffmpeg
from pytube import YouTube
from pytube.streams import Stream
from slugify import slugify

VIDEO_ITAGS = [137, 136, 135, 134, 133, 160]
AUDIO_ITAGS = [140, 139]


def to_hh_mm_ss(time: Union[int, str, None]) -> str:
    """
    Convert any time defined as a string or seconds to the HH:MM:SS format
    """
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


def get_video_id(url: str) -> Union[str, None]:
    """
    Extracts the ID from any YouTube-like url
    """
    parts = urlparse(url)
    if parts.netloc in {"www.youtube.com", "youtube.com"}:
        if parts.path == "/watch":
            return parse_qs(parts.query)["v"][0]
    elif parts.netloc == "youtu.be":
        return parts.path.lstrip("/")
    else:
        return None


def get_audio_stream(video):
    mime_type = "audio/mp4"
    streams = [stream for stream in video.streams.filter(only_audio=True) if stream.mime_type == mime_type]
    sorted_streams = sorted(
        streams, key=lambda stream: 1000 if stream.itag not in AUDIO_ITAGS else AUDIO_ITAGS.index(stream.itag)
    )
    return sorted_streams[0]


def get_video_streams(video: YouTube) -> Stream:
    mime_type = "video/mp4"
    streams = [stream for stream in video.streams.filter(only_video=True) if stream.mime_type == mime_type]
    sorted_streams = sorted(
        streams, key=lambda stream: 1000 if stream.itag not in VIDEO_ITAGS else VIDEO_ITAGS.index(stream.itag)
    )
    return sorted_streams[0]


def download_audio_only(original_name, yt) -> Path:
    audio_file = f"{original_name}_audio.mp4"
    audio = get_audio_stream(yt)
    audio.download(filename=audio_file)
    return Path(audio_file)


def download_video_only(original_name, yt) -> Path:
    video_file = f"{original_name}_video.mp4"
    video = get_video_streams(yt)
    video.download(filename=video_file)
    return Path(video_file)


def download_video(
    video_id: str, start_time: Optional[str] = None, end_time: Optional[str] = None, keep: bool = False
) -> YouTube:
    yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    name_slug = slugify(yt.title)

    base_name = f"{name_slug}__{video_id}"
    video_file = download_video_only(base_name, yt)
    audio_file = download_audio_only(base_name, yt)

    try:
        ffmpeg_processing(audio_file, video_file, base_name, end_time, start_time)
        if not keep:
            audio_file.unlink()
            video_file.unlink()
    except FileNotFoundError:
        logging.warning("No ffmpeg is not available")

    return yt


def ffmpeg_processing(
    audio_file: Path,
    video_file: Path,
    original_name: str,
    end_time: Optional[str] = None,
    start_time: Optional[str] = None,
) -> None:

    ffmpeg_arguments = {}
    if start_time:
        ffmpeg_arguments["ss"] = start_time
    if end_time:
        ffmpeg_arguments["to"] = end_time
    input_video = ffmpeg.input(str(video_file), **ffmpeg_arguments)
    input_audio = ffmpeg.input(str(audio_file), **ffmpeg_arguments)
    ffmpeg.concat(input_video, input_audio, v=1, a=1).output(
        f"./{original_name}.mp4",
    ).run(quiet=True, overwrite_output=True)
