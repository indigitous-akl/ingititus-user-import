
Installation
============

## Docker

Linux: https://runnable.com/docker/install-docker-on-linux
Mac: https://docs.docker.com/docker-for-mac/install/

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


Learning Gremlin
================

http://tinkerpop.apache.org/docs/current/reference/

Try out the following (from the above URL):
```java
gremlin> graph = TinkerFactory.createModern() //1
==>tinkergraph[vertices:6 edges:6]
gremlin> g = graph.traversal()        //2
==>graphtraversalsource[tinkergraph[vertices:6 edges:6], standard]
gremlin> g.V().has('name','marko').out('knows').values('name') //3
==>vadas
==>josh
```


<img src="http://tinkerpop.apache.org/docs/current/images/tinkerpop-classic-ex1.png" alt="Gremlin Example Graph" width="500">
