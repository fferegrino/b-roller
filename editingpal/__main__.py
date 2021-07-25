import typer
from pytube import YouTube
from slugify import slugify

from editingpal.giphy.gif import download_giphy

app = typer.Typer(add_completion=False)


@app.command()
def video(url: str):
    yt = YouTube(url)
    title = slugify(yt.title)
    audio_streams = yt.streams.filter(only_video=True)
    streams = [(stream.itag, int(stream.resolution[:-1])) for stream in audio_streams if stream.mime_type=="video/mp4"]
    max_res_itag = sorted(streams, key=lambda str: str[1], reverse=True)[0][0]
    yt.streams.get_by_itag(max_res_itag).download(filename=title)


@app.command()
def audio(url: str):
    yt = YouTube(url)
    title = slugify(yt.title)
    audio_streams = yt.streams.filter(only_audio=True)
    [mp4] = [stream for stream in audio_streams if stream.mime_type=="audio/mp4"]
    mp4.download(filename=title)


@app.command()
def gif(url: str):
    download_giphy(url)



if __name__ == "__main__":
    app()
