# B-Roller

Download B-roll footage from YouTube **for fair use purposes**.

## Usage

### Download from YouTube

```
broll yt [OPTIONS] URL [START] [END]

  Download content from YouTube

Arguments:
  URL      A video id or a YouTube short/long url  [required]
  [START]  The desired start of the video in seconds or the format 00:00:00
  [END]    The desired end of the video in seconds or the format 00:00:00
```

For example:

```shell
broll yt "https://www.youtube.com/watch?v=QFLiIU8g-R0" 00:10 00:17
```
