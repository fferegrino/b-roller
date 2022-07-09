import ffmpeg
from pytube import YouTube
from pytube.streams import Stream
from slugify import slugify

video_itags = [137, 136, 135, 134, 133, 160]
audio_itags = [140, 139]


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


def download_video(video_id: str):
    video = YouTube(f"https://www.youtube.com/watch?v={video_id}")
    name_slug = slugify(video.title)

    audio = get_streams(video, "audio")
    video = get_streams(video, "video")

    original_name = f"{name_slug}__{video_id}"

    audio_file = f"{original_name}_audio.mp4"
    video_file = f"{original_name}_video.mp4"

    audio.download(filename=audio_file)
    video.download(filename=video_file)

    input_video = ffmpeg.input(video_file)
    input_audio = ffmpeg.input(audio_file)
    ffmpeg.concat(input_video, input_audio, v=1, a=1).output(f"./{original_name}.mp4").run()
