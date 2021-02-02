import json
import os
import youtube_dl
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError

class DownloadResult:
    def __init__(self, error=False, info={}, code=0, exception=None): 
        self._error = error
        self.info = info
        self.fname = info.get("_filename")
        self.code = code
        self.exception = exception

    @property
    def thumbnail(self):
        return self.info.get("thumbnail")

    @property
    def duration(self):
        return self.info.get("duration", 0)

    @property
    def title(self):
        return self.info.get("title", "Unknown Title")

    @property
    def error(self):
        return self._error or self.code

    @property
    def error_message(self):
        return str(self.code) if self.code else str(self.exception)


def download(item, test=False):
    opts = {}
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(item.url, download=False)

        item.title = info.get("title", "Unknown")
        item.thumbnail = info.get("thumbnail")

        if test:
            return DownloadResult(info=info)
        else:
            opts['outtmpl'] = f"./videos/{item.uuid}.%(ext)s"
            with YoutubeDL(opts) as ydl:
                code = ydl.download([item.url])
            return DownloadResult(info=info, code=code)

    except DownloadError as e:
        return DownloadResult(error=True, exception=e)
