# Magnet2Torrent

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![CodeFactor](https://www.codefactor.io/repository/github/usma0118/magnet2torrent/badge)](https://www.codefactor.io/repository/github/usma0118/magnet2torrent)
[![CodeQL](https://github.com/usma0118/magnet2torrent/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/usma0118/magnet2torrent/actions/workflows/codeql-analysis.yml)
[![Docker release](https://github.com/usma0118/magnet2torrent/actions/workflows/build-docker-image.yml/badge.svg?branch=main)](https://github.com/usma0118/magnet2torrent/actions/workflows/build-docker-image.yml)

A Python based tool that converts magnet links to .torrent files.

**Looking for a way to contribute? Please find issues with the [help-wanted] label
or to improve documentation [docs-needed], thank you.**

[help-wanted]: https://github.com/usma0118/magnet2torrent/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22
[docs-needed]: https://github.com/usma0118/magnet2torrent/issues?q=label%3A%22docs+needed%22+sort%3Aupdated-desc

## Features

- Monitors blackhole folder for new magnet links and convert them to torrents
- Adds torrent trackers to torrents to increase download chances

## Setup and installation

The script has been tested to work with Python 3.xx versions

Recommended way is to run it as [docker container](https://hub.docker.com/repository/docker/antaresinc/magnet2torrent)

### Environment Variables

- `log_level` (`info`) : can be set to info,warning, error
- `trackers` (default is using [ngosang/trackerslist](https://github.com/ngosang/trackerslist)) 

#### **Blackhole**

- `magnet_watch` (docker exposes `/torrent` as volume) Directory path to monitor for new magnet links
- `torrent_blackhole` (optional, defaults to same value as `magnet_watch`) must be set to same blackhole directory as your torrent client.

#### **Web server**
- `webserver_basepath` (`/`)
- `webserver_port` (`8080`)
- `webserver_secret` (defaults to randmon generated))

### **Proxy**

Application supports http proxy for fetching torrent info

- `proxy_hostname` (`optional`)
- `proxy_port` (`required` if proxy hostname is set)
- `proxy_username` (`optional`)
- `proxy_password` (`optional`)

#### Docker Compose


## Licenses

All code is licensed under the [GPL version 3](http://www.gnu.org/licenses/gpl.html)

This has been greatly inspired by [Magnet2Torrent](https://github.com/danfolkes/Magnet2Torrent)
