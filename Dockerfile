FROM python:3.11.0a2-alpine3.15 AS python-alpine3
# Setup env
## Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
## Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND noninteractive

FROM python-alpine3 AS python-deps
RUN python3 -m pip install --upgrade pip setuptools wheel --no-cache-dir
RUN python3 -m pip install pipenv --no-cache-dir
#RUN pip install pipenv --no-cache-dir

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