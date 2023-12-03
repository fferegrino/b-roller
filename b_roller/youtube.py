import hashlib
import logging
import shutil
from importlib import resources as importlib_resources
from pathlib import Path
from typing import Optional, Union
from urllib.parse import parse_qs, urlparse

import ffmpeg
from PIL import Image, ImageDraw, ImageFont
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


def make_watermark(watermark_text: str):
    hashed_text = hashlib.md5(watermark_text.encode()).hexdigest()
    watermark_file = cache / f"{hashed_text}.png"

    if watermark_file.exists():
        logger.info("Using cached watermark")
        return watermark_file

    back_ground_color = (230, 230, 230, 0)
    white_font_color = (255, 255, 255, 255)
    black_font_color = (0, 0, 0, 255)
    font_size = 35
    shadow_offset = 2

    padding = 20
    img = Image.new("RGBA", (1, 1), back_ground_color)
    draw = ImageDraw.Draw(img)
    with importlib_resources.path("b_roller.fonts", "Oswald-Medium.ttf") as font_path:
        font = ImageFont.truetype(str(font_path), font_size)

    (top, left, bottom, right) = draw.textbbox((0, 0), watermark_text, font=font)

    img = Image.new(
        "RGBA", (shadow_offset + bottom + (2 * padding), shadow_offset + right + (2 * padding)), back_ground_color
    )
    draw = ImageDraw.Draw(img)
    draw.text((padding + shadow_offset, padding + shadow_offset), watermark_text, black_font_color, font=font)
    draw.text((padding, padding), watermark_text, white_font_color, font=font)

    img.save(str(watermark_file), "PNG")
    return watermark_file


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


def download_video_only(original_name, yt, watermark_file) -> Path:
    watermarked_file_name = cache / f"wm_{original_name}_video.mp4"
    in_file_name = cache / f"original_{original_name}_video.mp4"

    logger.debug("Downloading video")
    if watermarked_file_name.exists():
        logger.info("Using watermarked cached video")
        return watermarked_file_name

    if in_file_name.exists():
        logger.info("Using cached video")
        return in_file_name

    video = get_video_streams(yt)
    video.download(filename=in_file_name)

    try:
        logger.info("Adding watermark")

        ffmpeg.input(in_file_name).output(
            str(watermarked_file_name),
            vf="movie=" + str(watermark_file) + " [watermark]; [in][watermark] overlay=W-w-0:H-h-0 [out]",
        ).run(quiet=True, overwrite_output=True)
    except FileNotFoundError:
        logging.warning("No ffmpeg is not available")
        return Path(in_file_name)

    return Path(watermarked_file_name)


def download_video(
    video_id: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    kind: str = "both",
    output_path: Optional[Path] = None,
    name: Optional[str] = None,
) -> YouTube:
    start_time = to_hh_mm_ss(start_time)
    end_time = to_hh_mm_ss(end_time)

    yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    name_slug = slugify(yt.title)

    base_name = f"{name_slug}__{video_id}"

    extension = "mp3" if kind == "audio" else "mp4"

    watermark_file = make_watermark(f"youtu.be/{video_id} - {yt.title}")

    if kind == "both":
        video_file = download_video_only(base_name, yt, watermark_file)
        audio_file = download_audio_only(base_name, yt)
        try:
            logger.info("Merging audio and video")
            result = concatenate_video(audio_file, video_file, base_name)
            result = trim_video(result, end_time, start_time)
        except FileNotFoundError:
            logging.warning("No ffmpeg is not available")
    elif kind == "audio":
        result = download_audio_only(base_name, yt)
        result = repackage_audio(result)
    elif kind == "video":
        result = download_video_only(base_name, yt, watermark_file)
        result = trim_video(result, end_time, start_time)

    final_name = name or base_name
    output_file = (output_path or Path.cwd()) / f"{final_name}.{extension}"
    logger.debug(f"Downloaded to {output_file}")
    shutil.copy(result, output_file)

    return yt


def repackage_audio(audio_file: Path) -> Path:
    logger.info("Repackaging audio")
    result = cache / f"{audio_file.stem}_repackaged.mp3"
    if result.exists():
        logger.info("Using cached result")
        return result
    ffmpeg.input(str(audio_file)).output(str(result)).run(quiet=True, overwrite_output=True)
    return result


def concatenate_video(
    audio_file: Path,
    video_file: Path,
    original_name: str,
) -> Path:
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
        ).run(quiet=True, overwrite_output=True)

        video_file = result

    return video_file
