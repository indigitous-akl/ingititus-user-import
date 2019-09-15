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

    def get_forks(self, login, pagination=100):
        user_forks = []
        hasNextPage = True

        repositories_search_string = 'repositories(isFork: true first: {})'.format(pagination)

        # TODO: Don't search, just query user directly
        while hasNextPage:
            full_query_string = """
                query User ($login: String!){
                  user(login: $login) {
                    id
                    """ + repositories_search_string + """ {
                      totalCount
                      edges {
                        node {
                          nameWithOwner
                          id
                          parent {
                            nameWithOwner
                            id
                            owner {
                              login
                              id
                            }
                            primaryLanguage {
                              id
                              name
                            }
                          }
                          primaryLanguage {
                            id
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
                }"""

            #print(full_query_string)

            result = json.loads(self.client.execute(full_query_string, variables={'login': login}))
            #print(result)
            forks = result['data']['user']['repositories']
            for fork in forks['edges']:
                # basic fork details
                name = fork['node']['nameWithOwner']
                fork_id = fork['node']['id']
                if fork['node']['primaryLanguage']:
                    language = fork['node']['primaryLanguage']['name']
                    language_id = fork['node']['primaryLanguage']['id']
                else:
                    language = None
                    language_id = None

                # fork parent details
                # 'fork' ->- FORKS ->-'parent'
                fork_parent_repo = fork['node']['parent']
                if not fork_parent_repo:
                    continue
                fork_parent_repo_name = fork_parent_repo['nameWithOwner']
                fork_parent_repo_id = fork_parent_repo['id']
                fork_parent_repo_owner_login = fork_parent_repo['owner']['login']
                if fork_parent_repo['primaryLanguage']:
                    fork_parent_repo_language = fork_parent_repo['primaryLanguage']['name']
                    fork_parent_repo_language_id = fork_parent_repo['primaryLanguage']['id']
                else:
                    fork_parent_repo_language = None
                    fork_parent_repo_language_id = None

                user_forks.append({'name': name, 'id': fork_id, 'language': language})
                print("{} ({}) - forks {}/{} ({})".format(name, language, fork_parent_repo_owner_login, fork_parent_repo_name, fork_parent_repo_language))
                self.gremlin.add_fork(fork_id, login, name, language, language_id, fork_parent_repo_id, fork_parent_repo_name, fork_parent_repo_language, fork_parent_repo_language_id)

            hasNextPage = forks['pageInfo']['hasNextPage']
            repositories_search_string = 'repositories(isFork: true first: {} after: "{}")'.format(pagination, forks['pageInfo']['endCursor'])

        return user_forks


if __name__ == "__main__":
    fork_fetcher = ForkFetcher(os.environ['GITHUB_TOKEN'])
    github_users = fork_fetcher.gremlin.get_github_users()

    # for debug
    skips = []

    for login in github_users:
        if login in skips:
            print("Skipping {}".format(login))
            continue
        print(login)
        fork_fetcher.get_forks(login)

