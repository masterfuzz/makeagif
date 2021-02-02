import threading
import makeagif.util.ytdownloader as ytdownloader
import makeagif.util.ffgif as ffgif
from makeagif.giftask import GifTask, Status
from queue import Queue
import bottle
from bottle import route, request


download_queue = Queue(20)
process_queue = Queue(20)
tasks = {}

@route("/")
def main():
    return bottle.template("tpl/form.htm")

@route("/submit")
def submit_task():
    gt = GifTask.from_query(request.query)
    tasks[str(gt.uuid)] = gt
    download_queue.put(gt, timeout=60)
    
    # return f'Your request has been submitted for processing. Watch status <a href="/tasks/{gt.uuid}">here</a>'
    bottle.redirect(f"/tasks/{gt.uuid}")

@route("/tasks")
def list_tasks():
    return {"tasks": [gt.to_dict() for gt in tasks.values()], "count": len(tasks)}

@route("/tasks/<uuid>")
def task_detail(uuid):
    if uuid in tasks:
        return bottle.template("tpl/task_detail.htm", t=tasks[uuid])
    else:
        raise bottle.HTTPError(status=404)

# gifs!
@route("/gifs/<uuid>")
def gifs(uuid):
    return bottle.static_file(f"{uuid}.gif", root="./gifs")

# workers
def dl_worker():
    while True:
        item = download_queue.get()
        print(f"dl_worker: get {str(item)}")
        item.status = Status.Downloading

        result = ytdownloader.download(item)

        if result.error:
            print(f"dl_worker: failed to download item. exit code {result.code}")
            # with open(f"./logs/{str(item.uuid)}.log", 'w') as fh:
            #     result.dump(fh)

            item.status = Status.Error
            item.error_message = result.error_message
        else:
            item.thumbnail = result.thumbnail
            item.source_duration = result.duration
            item.title = result.title
            item.source_fname = result.fname

            item.status = Status.Ready

            print(f"dl_worker: done {str(item)}")
            process_queue.put(item)
        download_queue.task_done()

def process_worker():
    while True:
        item = process_queue.get()
        print(f"pr_worker: get {str(item)}")
        # pretend to process
        item.status = Status.Processing
        res = ffgif.process(item)
        if res.error:
            print(f"pr_worker: failed to process item.")
            print(res.exception)
            with open(f"./logs/{str(item.uuid)}.log", 'w') as fh:
                res.dump(fh)

            item.status = Status.Error
            item.error_message = str(res.exception)
        else:
            print(f"pr_worker: done {str(item)}")
            item.status = Status.Done
        process_queue.task_done()

def start_workers():
    threading.Thread(target=dl_worker, daemon=True).start()
    threading.Thread(target=process_worker, daemon=True).start()

if __name__ == "__main__":
    start_workers()
    bottle.run(host="0.0.0.0", port=8080)
