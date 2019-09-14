#!/usr/bin/env python

import json
import os
import sys
from graphqlclient import GraphQLClient

from gremlin_wrapper import GremlinWrapper

class ForkFetcher(object):
    def __init__(self, github_token):
        self.client = GraphQLClient("https://api.github.com/graphql")
        self.client.inject_token("bearer " + github_token)
        gremlin_url = os.environ['GREMLIN_URL']
        self.gremlin = GremlinWrapper(gremlin_url)

    def get_forks(self, email, pagination=100):
        user_forks = []
        hasNextPage = True

        query_search_string = 'search(query: "{}", type: USER, first: 1)'.format(email)
        repositories_search_string = 'repositories(isFork: true first: {})'.format(pagination)

        while hasNextPage:
            full_query_string = """{
             """ + query_search_string + """ {
                userCount
                edges {
                  node {
                    ... on User {
                      name
                      login
                      id
                      """ + repositories_search_string + """ {
                        totalCount
                        edges {
                          node {
                            name
                            id
                            parent {
                              name
                              id
                              owner {
                                login
                              }
                              primaryLanguage {
                                name
                              }
                            }
                            primaryLanguage {
                              name
                            }
                          }
                        }
                        pageInfo {
                          endCursor
                          hasNextPage
                        }
                      }
                    }
                  }
                }
              }
            }"""
            result = json.loads(self.client.execute(full_query_string))
            forks = result['data']['search']['edges'][0]['node']['repositories']
            for fork in forks['edges']:
                # basic fork details
                name = fork['node']['name']
                fork_id = fork['node']['id']
                if fork['node']['primaryLanguage']:
                    language = fork['node']['primaryLanguage']['name']
                else:
                    language = None

                # fork parent details
                # 'fork' ->- FORKS ->-'parent'
                fork_parent_repo = fork['node']['parent']
                fork_parent_repo_name = fork_parent_repo['name']
                fork_parent_repo_id = fork_parent_repo['id']
                fork_parent_repo_owner_login = fork_parent_repo['owner']['login']
                if fork_parent_repo['primaryLanguage']:
                    fork_parent_repo_language = fork['node']['primaryLanguage']['name']
                else:
                    fork_parent_repo_language = None

                user_forks.append({'name': name, 'id': fork_id, 'language': language})
                print("{} ({}) - forks {}/{} ({})".format(name, language, fork_parent_repo_owner_login, fork_parent_repo_name, fork_parent_repo_language))
                print(email)
                self.gremlin.add_fork(fork_id, email, name, language, fork_parent_repo_id, fork_parent_repo_name, fork_parent_repo_language)

            hasNextPage = forks['pageInfo']['hasNextPage']
            repositories_search_string = 'repositories(isFork: true first: {} after: "{}")'.format(pagination, forks['pageInfo']['endCursor'])

        return user_forks


if __name__ == "__main__":
    email = sys.argv[1]
    fork_fetcher = ForkFetcher(os.environ['GITHUB_TOKEN'])
    result = fork_fetcher.get_forks(email)
