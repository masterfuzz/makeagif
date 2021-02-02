import os
import glob
import ffmpeg
# from makeagif import GifTask

class Result:
    def __init__(self, stdout=None, stderr=None, exception=None):
        self.stdout = stdout
        self.stderr = stderr
        self.exception = exception

    @property
    def error(self):
        if self.exception:
            return True
        return False

    def dump(self, fh):
        if self.stdout:
            fh.write(self.stdout.decode())
        if self.stderr:
            fh.write(self.stderr.decode())
        if self.exception:
            fh.write(str(self.exception))

class MockItem:
    uuid = "074df9d3-9e48-4847-8005-60e068215060"
    source_fname = "how are you doing that with your mouth-lQIFC__VOUo.mkv"
    start = 0
    end = 10
    size = 480
    fps = 24

def process(item) -> Result:
    if os.path.isfile(f"./gifs/{item.uuid}.gif"):
        return Result(stdout=b"File exists")
    try:
        # s = ffmpeg.input(f"./videos/{item.source_fname}")
        fname = list(glob.glob(f"./videos/{item.uuid}*"))[0]
        s = ffmpeg.input(fname)
        if item.end:
            s = ffmpeg.trim(s, start=item.start, end=item.end)
        else:
            s = ffmpeg.trim(s, start=item.start)

        s = ffmpeg.filter(s, 'fps', fps=item.fps)
        s = ffmpeg.filter(s, 'scale', item.size, -1)
        split = ffmpeg.filter_multi_output(s, "split")
        p = ffmpeg.filter(split[0], "palettegen")
        s = ffmpeg.filter([split[1], p], filter_name="paletteuse")

        o = ffmpeg.output(s, f"./gifs/{item.uuid}.gif")
        out, err = o.run(quiet=True)
        return Result(stderr=err, stdout=out)

    except Exception as e:
        if hasattr(e, "stderr"): 
            return Result(exception=e, stderr=e.stderr, stdout=e.stdout)
        else:
            return Result(exception=e)
