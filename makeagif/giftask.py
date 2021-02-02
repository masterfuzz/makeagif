from enum import Enum
from datetime import timedelta
from uuid import uuid4

class Status(Enum):
    New = 1
    Downloading = 2
    Ready = 3
    Processing = 4
    Done = 5
    Error = 6

def td_str(td):
    return str(timedelta(seconds=td))

class GifTask:
    def __init__(self, url, start=0, end=0, size=480, fps=24):
        self.url = url
        self.start, self.end = int(start), int(end)
        self.size = size
        self.fps = fps
        self.uuid = uuid4()
        self.status = Status.New
        self.source_duration = 0
        self.thumbnail = ""
        self.title = str(self.uuid)
        self.error_message = None
        self.source_fname = None

    def __str__(self):
        return f"GifTask<{self.status}: '{self.url}'>"

    def to_dict(self):
        return {
            "url": self.url,
            "start": td_str(self.start),
            "end": td_str(self.end),
            "source_duration": self.source_duration,
            "quality": f"{self.size}w @{self.fps}fps",
            "uuid": str(self.uuid),
            "status": str(self.status),
            "thumbnail": self.thumbnail,
            "title": self.title,
            "_ref": f"/tasks/{self.uuid}"
        }

    @staticmethod
    def from_query(query):
        return GifTask(
            query.url, query.start, query.end, query.size, query.fps
        )

    @property
    def done(self):
        return self.status == Status.Done
