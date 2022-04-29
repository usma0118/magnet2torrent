FROM python:3.10-alpine3.15 AS python-alpine3
# Setup env
## Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
## Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND noninteractive

FROM python-alpine3 AS python-deps
RUN python3 -m pip install --upgrade pip setuptools wheel --no-cache-dir
RUN python3 -m pip install pipenv --no-cache-dir

RUN apk add gcc

# BUG: https://github.com/pypa/pipenv/issues/4564
# gist: https://gist.github.com/orenitamar/f29fb15db3b0d13178c1c4dd611adce2
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN apk --no-cache --update-cache add gcc gfortran build-base wget freetype-dev libpng-dev openblas-dev
RUN pip install --no-cache-dir numpy
#scipy pandas matplotlib

WORKDIR /app
COPY Pipfile* ./

RUN pipenv install --deploy --ignore-pipfile

FROM python-alpine3 as runtime
ENV magnet_watch=/torrent
VOLUME [ $magnet_watch ]
ENV log_level="info"
ENV FLASK_ENV=production
# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 1001  magnet2torrent --disabled-password --no-create-home --gecos ""
COPY --from=python-deps /root/.local/share/virtualenvs/app-*/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

COPY --chown=magnet2torrent:magnet2torrent . /app

WORKDIR /app

EXPOSE 8080

USER magnet2torrent

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "main.py","--monitor"]