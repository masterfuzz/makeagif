FROM python:3

WORKDIR /usr/src/app

COPY bottle.requirements.txt /requirements.txt

RUN apt update && apt install -y ffmpeg
RUN pip install --no-cache-dir -r /requirements.txt

COPY makeagif/ ./makeagif/
COPY tpl/ ./tpl/

RUN mkdir -p ./gifs ./logs ./videos

EXPOSE 8080

CMD [ "python", "-m", "makeagif.web" ]
