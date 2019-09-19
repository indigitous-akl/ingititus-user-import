#!/usr/bin.env python
from gremlin_python import statics
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.driver.protocol import GremlinServerError
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
        return self.g.V() \
        .has('indigitous_user', 'uid', uid) \
        .fold() \
        .coalesce(
            unfold(),
            addV('indigitous_user') \
            .property('name', name) \
            .property('uid', uid) \
            .property('email', email) \
            .property('login', login)) \
        .next()

    def add_github_user(self, login, email, name, uid):
        # add a user to the gremlin graph
        if name is None:
            return self.g.V().has('github_user', 'uid', uid) \
            .fold() \
            .coalesce(
                unfold(),
                addV('github_user')
                .property('uid', uid) \
                .property('email', email) \
                .property('login', login)) \
            .next()
        else:
            return self.g.V().has('github_user', 'uid', uid) \
            .fold() \
            .coalesce(
                unfold(),
                addV('github_user')
                .property('name', name) \
                .property('uid', uid) \
                .property('email', email) \
                .property('login', login)) \
            .next()


    def add_repo(self, repo_id, name_with_owner, language_name, language_id, login=None):
        # get user by email to add "owns" edge
        language = self.add_language(language_name, language_id)
        repo = self.g.V().has('repository', 'uid', repo_id) \
        .fold() \
        .coalesce(
            unfold(),
            addV('repository')
            .property('name', name_with_owner) \
            .property('uid', repo_id)) \
        .next()

        # repository has primary language
        if language_name:
            #print("Trying to add edge between {} and {}".format(name_with_owner, language_name))
            try:
                self.g.V(repo).addE('primary_language').to(language).next()
            except GremlinServerError:
                pass
            #self.g.V(repo).as_('v').V(language).coalesce(__.inE('primary_language').where(outV().as_('v')), addE('primary_language').from_('v'))

        if login:
            user = self.g.V().has('github_user', 'login', login).next()
            # user owns repo
            try:
                self.g.V(user).addE('owns').to(repo).next()
            except GremlinServerError:
                pass

        return repo


    def add_language(self, language, uid):
        #print("Adding language {} ({})".format(language, uid))
        if not language:
            #print("Returning early")
            return
        return self.g.V().has('language', 'uid', uid) \
        .fold() \
        .coalesce(
            unfold(),
            addV('language')
            .property('name', language) \
            .property('uid', uid)) \
        .next()

    def add_repository(self, nameWithOwner):
        # add a user to the gremlin graph
        return self.g.V() \
        .has('repository', 'nameWithOwner', nameWithOwner) \
        .fold() \
        .coalesce(
            unfold(),
            addV('github_user') \
            .property('nameWithOwner', nameWithOwner)) \
        .iterate()


    def get_list_of_indigitous_users(self):
        #get a list of all people through name property.
         return self.g.V() \
                .hasLabel('indigitous_user') \
                .group() \
                    .by(__.id()) \
                    .by('email') \
                .toList()

    def get_github_users(self):
        #get a list of all people through name property.
         return self.g.V() \
                .hasLabel('github_user') \
                .values('login') \
                .toList()

    def get_github_indigitous_users_by_github_login(self):
        #get a list of all people through name property.
         return self.g.V() \
                .hasLabel('indigitous_user') \
                .out('is') \
                .hasLabel('github_user') \
                .group() \
                    .by(__.id()) \
                    .by('login') \
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

    # TODO: use objects instead of passing around strings
    def add_fork(self, repo_id, login, name_with_owner, language, language_id, parent_repo_id, parent_repo_name_with_owner, parent_repo_language, parent_repo_language_id):
        fork = self.add_repo(repo_id, name_with_owner, language, language_id, login=login)
        parent = self.add_repo(parent_repo_id, parent_repo_name_with_owner, parent_repo_language, parent_repo_language_id)
        try:
            self.g.V(fork).addE('forks').to(parent).next()
        except GremlinServerError:
            pass
        return fork


    def close(self):
        self.remote_connection.close()
