#!/usr/bin/env python

import json
import os
from email_validator import validate_email, EmailNotValidError
from graphqlclient import GraphQLClient

from insert_user_gremlin import GremlinInserter

client = GraphQLClient("https://api.github.com/graphql")
client.inject_token("bearer " + os.environ['GITHUB_TOKEN'])

def get_random_users(num_users, query="test"):
    page_size = num_users
    users = []

    query_search_string = 'search(query: "{}", type: USER, first: {})'.format(query, page_size)

    gremlin_inserter = GremlinInserter("ws://localhost:8182/gremlin")

    count = 0;
    while (count < num_users):
        full_query_string = """
        {
          """ + query_search_string + """ {
            userCount
            edges {
              node {
                ... on User {
                  login
                  name
                  email
                  id
                }
              }
            }
            pageInfo {
              endCursor
              hasNextPage
            }
          }
        }
        """
        result = json.loads(client.execute(full_query_string))

        try:
            users_list = result['data']['search']['edges']

            for user in users_list:
                if user['node']:
                    #print(user)
                    email = user['node']['email']
                    login = user['node']['login']
                    name = user['node']['name']
                    uid = user['node']['id']
                    if not email:
                        continue
                    if not name:
                        continue
                    try:
                        v = validate_email(email)
                        email = v['email']
                    except EmailNotValidError:
                        continue
                    users.append({'login': login, 'name': name, 'email': email, 'uid': uid})
                    gremlin_inserter.add_indigitous_user(login, email, name, uid)
                    count+=1

            page_info = result['data']['search']['pageInfo']
            endCursor = page_info['endCursor']
            if page_info['hasNextPage']:
                #print("Next Page, cursor: {}".format(endCursor))
                query_search_string = 'search(query: "{}", type: USER, first: {} after: "{}")'.format(query, page_size, endCursor)
            else:
                break
        except KeyError:
            print(json.dumps(result))

    gremlin_inserter.close()
    return users

if __name__ == "__main__":
    users = get_random_users(20, query="a")
    for user in users:
        print("{} ({}): {} {}".format(user['login'], user['name'], user['email'], user['uid']))
