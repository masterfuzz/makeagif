FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt /requirements.txt
RUN set -ex \
    && BUILD_DEPS=" \
    build-essential \
    libpcre3-dev \
    libpq-dev \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && pip install --no-cache-dir -r /requirements.txt \
    \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*

COPY makeagif/ ./makeagif/
COPY tpl ./tpl/
# RUN mkdir -p out && mkdir -p json-cache
COPY uwsgi-http.ini ./
COPY makeagif.wsgi ./

RUN mkdir -p ./gifs ./logs ./videos

EXPOSE 3031 9191

CMD [ "uwsgi", "uwsgi-http.ini" ]
