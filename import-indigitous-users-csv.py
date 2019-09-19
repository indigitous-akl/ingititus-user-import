#!/usr/bin/env python

import json
import os
import csv
import sys
#from email_validator import validate_email, EmailNotValidError
from gremlin_wrapper import GremlinWrapper

gremlin_url = os.environ['GREMLIN_URL']
gremlin = GremlinWrapper(gremlin_url)

with open(sys.argv[1], newline='') as csvfile:
     spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
     for row in spamreader:
        uid = row[0]
        login = row[2]
        email = row[3]
        name = row[4]
        print("login:{}, email:{}, name:{}, uid:{}".format(login, email, name, uid))
        gremlin.add_indigitous_user(login, email, name, uid)

gremlin.close()
