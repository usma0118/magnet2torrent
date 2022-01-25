#!/bin/bash
DOCKER_BUILDKIT=1 docker build . -t antaresinc/magnet2torrent:1.0.0 -t antaresinc/magnet2torrent:latest
docker push antaresinc/magnet2torrent -a
