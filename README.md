
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

    # [If docker-compose not installed] pip install docker-compose

## Gremlin

    export GREMLIN_URL="ws://10.1.1.70:8182/gremlin"

    # [or add to .bashrc]


To Run
======

    docker-compose -f docker-compose-cql-es-consoleonly.yml up -d
    docker attach jce-gremlin-consoleonly
