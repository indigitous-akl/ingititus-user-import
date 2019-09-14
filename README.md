
Installation
============

## Docker

Linux: https://runnable.com/docker/install-docker-on-linux

## Python Requirements

    pip install -r requirements.txt  # Make sure you do this for Python3, not python2

## Janisgraph

    git clone git@github.com:indigitous-akl/janusgraph-docker.git
    # [Or] git clone https://github.com/indigitous-akl/janusgraph-docker

    git checkout consoleonly
    docker pull bramford/janusgraph:0.4.0 && docker tag bramford/janusgraph:0.4.0 janusgraph/janusgraph:latest
    # [Optional] pip install docker-compose
    docker-compose -f docker-compose-cql-es-consoleonly.yml up -d

## Gremlin

    export GREMLIN_URL="ws://10.1.1.70:8182/gremlin"

To run
======

    docker attach jce-gremlin-consoleonly
