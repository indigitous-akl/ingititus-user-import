#!/usr/bin/env python

import os
import json
from gremlin_wrapper import GremlinWrapper
from graphqlclient import GraphQLClient
from gremlin_python import statics
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.traversal import T
from gremlin_python.process.traversal import Order
from gremlin_python.process.traversal import Cardinality
from gremlin_python.process.traversal import Column
from gremlin_python.process.traversal import Direction
from gremlin_python.process.traversal import Operator
from gremlin_python.process.traversal import P
from gremlin_python.process.traversal import Pop
from gremlin_python.process.traversal import Scope
from gremlin_python.process.traversal import Barrier
from gremlin_python.process.traversal import Bindings
from gremlin_python.process.traversal import WithOptions
from gremlin_python.driver.protocol import GremlinServerError

def userStarredRepos(login):
  return """
      user(login: {}) {
        starredRepositories(first: 100) {
          nodes {
            nameWithOwner
          }
        }
      }
    }
  """.format(login)

def getQL(param):
  client = GraphQLClient("https://api.github.com/graphql")
  token = "bearer " + os.environ['GITHUB_TOKEN']
  print(token)
  client.inject_token(token)

  gremlin_url = os.environ['GREMLIN_URL']
  gremlin = GremlinWrapper(connection)
  users = gremlin.get_github_indigitous_users_by_github_login()
  print(users)

  for vertex, login in users[0].items():
      if len(email) < 1:
        continue
      email = email[0]
      print(vertex)
      print(email)
      query = userStarredRepos(login)
      print(query)
      result = client.execute(query)
      print(result)
      obj = json.loads(result)
      print(obj)
      #{'data':{'search': {'nodes': [{'name': 'Agis Anastasopoulos', 'login': 'agis', 'email': 'a@xz0.org', 'id': 'MDQ6VXNlcjgyNzIyNA==', 'databaseId': 827224}]}}}
      if len(obj['data']['search']['nodes']) < 1:
        continue
      result = obj['data']['search']['nodes'][0]
      name = result['name']
      uid = result['id']
      name = result['email']
      login = result['login']
      gh_user_vertex = gremlin.add_github_user(login, email, name, uid)
      print(gh_user_vertex)
      try:
        gremlin.edge_vertices('is', indigitous_user_vertex, gh_user_vertex)
      except GremlinServerError:
        pass


getQL("tada")
