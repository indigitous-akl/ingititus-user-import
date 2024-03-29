#!/usr/bin.env python
from gremlin_python import statics
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.process.traversal import Barrier
from gremlin_python.process.traversal import Bindings
from gremlin_python.process.traversal import Cardinality
from gremlin_python.process.traversal import Column
from gremlin_python.process.traversal import Direction
from gremlin_python.process.traversal import Operator
from gremlin_python.process.traversal import Order
from gremlin_python.process.traversal import P
from gremlin_python.process.traversal import Pop
from gremlin_python.process.traversal import Scope
from gremlin_python.process.traversal import T
from gremlin_python.process.traversal import WithOptions

#remote_connection = DriverRemoteConnection('ws://localhost:8182/gremlin','g')
#g = traversal().withRemote(remote_connection)
#print("Vertices: {}".format(g.V().toList()))
#remote_connection.close()

class GremlinWrapper(object):
    def __init__(self, remote_gremlin_server):
        self.remote_server = remote_gremlin_server
        self.remote_connection = DriverRemoteConnection(remote_gremlin_server,'g')
        self.g = traversal().withRemote(self.remote_connection)
        statics.load_statics(globals())

    def add_indigitous_user(self, login, email, name, uid):
        # add a user to the gremlin graph
        self.g.V() \
        .has('indigitous_user', 'uid', uid) \
        .fold() \
        .coalesce(
            unfold(),
            addV('indigitous_user') \
            .property('name', name) \
            .property('uid', uid) \
            .property('email', email) \
            .property('login', login)) \
        .toList()

    def add_github_user(self, login, email, name, uid):
        # add a user to the gremlin graph
        return self.g.V().has('github_user', 'uid', uid) \
        .fold() \
        .coalesce(
            unfold(),
            addV('github_user')
            .property('name', name) \
            .property('uid', uid) \
            .property('email', email) \
            .property('login', login)) \
        .toList()

    def add_repository(self, name):
        # add a user to the gremlin graph
        return self.g.V() \
        .has('repository', 'name', name) \
        .fold() \
        .coalesce(
            unfold(),
            addV('github_user') \
            .property('name', name)) \
        .iterate()


    def get_list_of_indigitous_users(self):
        #get a list of all people through name property.
         return self.g.V() \
                .hasLabel('indigitous_user') \
                .group() \
                    .by(__.id()) \
                    .by('email') \
                .toList()

    def edge_vertices(self, label, from_v, to_v):
        # Edge vertices
        return self.g.E() \
        .hasLabel(label) \
        .where(outV().hasId(from_v)) \
        .where(inV().hasId(to_v)) \
        .fold() \
        .coalesce( \
            unfold(), \
            addE(label) \
            .from_(V(from_v)) \
            .to(V(to_v))) \
            .iterate()

    def close(self):
        self.remote_connection.close()
