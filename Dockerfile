FROM python:3.10-alpine3.15 AS python-slim
# Setup env
## Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
## Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

FROM python-slim AS python-deps

RUN pip install pipenv --no-cache-dir
WORKDIR /app
COPY Pipfile* ./
RUN pipenv install --deploy --ignore-pipfile

FROM python-slim AS compile
#ARG APP_VERSION=$APP_VERSION
#ENV APP_VERSION=$APP_VERSION
COPY . /app
WORKDIR /app
# Compile sources
RUN python -m compileall .
#\
#&& chmod -R a+rX,g-w .


FROM python-slim as runtime
VOLUME [ "/data" ]
ENV magnet_watch=/data
# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 1001  magnet2torrent --disabled-password --no-create-home --gecos ""
COPY --from=python-deps /root/.local/share/virtualenvs/app-*/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

WORKDIR /app
COPY --chown=magnet2torrent:magnet2torrent --from=compile /app .

USER magnet2torrent

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "magnettotorrent.py","--monitor"]