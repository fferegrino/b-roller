import typer
from pytube import YouTube
from slugify import slugify

from editingpal.giphy.giphy import download_giphy
from editingpal.pixabay.pixabay import download_pixabay_video

app = typer.Typer(add_completion=False)


@app.command()
def video(url: str):
    yt = YouTube(url)
    title = slugify(yt.title)
    streams = yt.streams.filter(only_video=True)
    streams = [(stream.itag, int(stream.resolution[:-1])) for stream in streams if stream.mime_type == "video/mp4"]
    max_res_itag = sorted(streams, key=lambda itags: itags[1], reverse=True)[0][0]
    yt.streams.get_by_itag(max_res_itag).download(filename=f"{title}_video.mp4")


@app.command()
def audio(url: str):
    yt = YouTube(url)
    title = slugify(yt.title)
    streams = yt.streams.filter(only_audio=True)
    mp4_streams = [stream for stream in streams if stream.mime_type == "audio/mp4"]
    streams = sorted(mp4_streams, key=lambda stream: int(stream.abr[:-4]), reverse=True)
    streams[0].download(filename=f"{title}_audio.mp4")


@app.command()
def pixabay(url: str):
    download_pixabay_video(url)


@app.command()
def gif(url: str):
    download_giphy(url)


if __name__ == "__main__":
    app()
