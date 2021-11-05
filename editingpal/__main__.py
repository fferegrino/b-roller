import typer

from editingpal.giphy import download_giphy
from editingpal.pixabay import download_pixabay_video
from editingpal.youtube import download_youtube_audio, download_youtube_video

app = typer.Typer(add_completion=False)


@app.command()
def video(url: str):
    download_youtube_video(url)


@app.command()
def audio(url: str):
    download_youtube_audio(url)


@app.command()
def pixabay(url: str):
    download_pixabay_video(url)


@app.command()
def giphy(url: str):
    download_giphy(url)


if __name__ == "__main__":
    app()
