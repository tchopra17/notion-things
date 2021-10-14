import argparse
import os
import json

# create a json file with token

parser = argparse.ArgumentParser(description='sets script to be ready for use')
parser.add_argument('--token',
                   action='store',
                   type=str,
                   required=True,
                   help='notion token')
parser.add_argument('--database',
                   action='store',
                   type=str,
                   required=True,
                   help='database id')
args = parser.parse_args()


data = {
    'token': args.token,
    'database': args.database
}

myJSON = json.dumps(data)
filepath = os.path.join('.', 'config.json')

with open(filepath, "w") as jsonfile:
    jsonfile.write(myJSON)
