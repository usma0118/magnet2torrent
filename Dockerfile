FROM python:3.10-alpine3.15 AS python-alpine3
# Setup env
## Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
## Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

FROM python-alpine3 AS python-deps

RUN pip install pipenv --no-cache-dir

WORKDIR /app
COPY Pipfile* ./

ENV DEBIAN_FRONTEND noninteractive
RUN apk add python3-dev gcc --no-cache && \
   rm -rf /var/lib/apk/*

RUN pipenv install --deploy --ignore-pipfile

FROM python-alpine3 as runtime
VOLUME [ "/torrent" ]
ENV magnet_watch=/torrent
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