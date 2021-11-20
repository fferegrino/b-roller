from pytube import YouTube
from slugify import slugify


def get_streams(url, only_video):
    yt = YouTube(url)
    title = slugify(yt.title)
    args = {}
    if only_video:
        args["only_video"] = True
        mime_type = "video/mp4"
    else:
        args["only_audio"] = True
        mime_type = "audio/mp4"

    streams = [stream for stream in yt.streams.filter(**args) if stream.mime_type == mime_type]
    return streams, title


def download_youtube_video(url, **kwargs):
    streams, title = get_streams(url, only_video=True)
    streams = sorted(streams, key=lambda stream: int(stream.resolution[:-1]), reverse=True)
    streams[0].download(filename=f"{title}_video.mp4")


def download_youtube_audio(url, **kwargs):
    streams, title = get_streams(url, only_video=False)
    streams = sorted(streams, key=lambda stream: int(stream.abr[:-4]), reverse=True)
    streams[0].download(filename=f"{title}_audio.mp4")
