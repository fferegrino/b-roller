import logging
import shutil
from pathlib import Path
from typing import Optional, Union
from urllib.parse import parse_qs, urlparse

import ffmpeg
from slugify import slugify

from b_roller.settings import cache
from pytube import YouTube
from pytube.streams import Stream

VIDEO_ITAGS = [137, 136, 135, 134, 133, 160]
AUDIO_ITAGS = [140, 139]

logger = logging.getLogger(__name__)


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
    audio_file = cache / f"{original_name}_audio.mp4"
    logger.debug("Downloading audio")
    if audio_file.exists():
        logger.info("Using cached audio")
        return audio_file
    audio = get_audio_stream(yt)
    audio.download(filename=audio_file)
    return Path(audio_file)


def download_video_only(original_name, yt) -> Path:
    video_file = cache / f"{original_name}_video.mp4"
    logger.debug("Downloading video")
    if video_file.exists():
        logger.info("Using cached video")
        return video_file
    video = get_video_streams(yt)
    video.download(filename=video_file)
    return Path(video_file)


def download_video(
    video_id: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    download: str = "both",
    output_path: Optional[Path] = None,
) -> YouTube:
    yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    name_slug = slugify(yt.title)

    base_name = f"{name_slug}__{video_id}"

    extension = "mp3" if download == "audio" else "mp4"

    if download == "both":
        video_file = download_video_only(base_name, yt)
        audio_file = download_audio_only(base_name, yt)
        try:
            logger.info("Merging audio and video")
            result = concatenate_video(audio_file, video_file, base_name)
            result = trim_video(result, end_time, start_time)
        except FileNotFoundError:
            logging.warning("No ffmpeg is not available")
    elif download == "audio":
        result = download_audio_only(base_name, yt)
        result = repackage_audio(result)
    elif download == "video":
        result = download_video_only(base_name, yt)
        result = trim_video(result, end_time, start_time)

    output_file = (output_path or Path.cwd()) / f"{base_name}.{extension}"
    logger.debug(f"Downloaded to {output_file}")
    shutil.copy(result, output_file)

    return yt


def repackage_audio(audio_file: Path) -> Path:
    logger.info("Repackaging audio")
    result = cache / f"{audio_file.stem}_repackaged.mp3"
    if result.exists():
        logger.info("Using cached result")
        return result
    ffmpeg.input(str(audio_file)).output(str(result)).run(quiet=False, overwrite_output=True)
    return result


def concatenate_video(
    audio_file: Path,
    video_file: Path,
    original_name: str,
) -> None:
    output_file = cache / f"{original_name}.mp4"
    if not output_file.exists():
        logger.info("Downloading video")

        input_video = ffmpeg.input(str(video_file))
        input_audio = ffmpeg.input(str(audio_file))

        ffmpeg.concat(input_video, input_audio, v=1, a=1).output(
            str(output_file),
        ).run(quiet=True, overwrite_output=True)

    return output_file


def trim_video(
    video_file: Path,
    end_time: Optional[str] = None,
    start_time: Optional[str] = None,
):
    ffmpeg_arguments = {}
    if start_time:
        ffmpeg_arguments["start"] = start_time
    if end_time:
        ffmpeg_arguments["end"] = end_time

    if ffmpeg_arguments:
        message = f"Trimming video from {start_time or '-'} to {end_time or '-'}"
        logger.info(message)
        result = cache / f"{video_file.stem}_trimmed.mp4"
        logger.debug(f"Original video: {video_file}")
        ffmpeg.input(str(video_file)).trim(**ffmpeg_arguments).setpts("PTS-STARTPTS").output(
            str(result),
        ).run(overwrite_output=True)

        video_file = result

    return video_file
