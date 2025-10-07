# !/usr/bin/env python4

import requests
import json
import argparse

parser = argparse.ArgumentParser(description="Show earthquake information")
parser.add_argument("--code", type=int, default=551, help="set 551(earthquake) or 552(tsunami). (default: 551)")
args = parser.parse_args()

#url = "https://api.p2pquake.net/v2/history"
url = "https://api-v2-sandbox.p2pquake.net/v2/history"
code = args.code
limit = 1
offset = 0
parameters = {"codes":code, "limit":limit, "offset":offset}

results = requests.get(url, params=parameters)
data_json = json.loads(results.text)

if code == 551:
    name = data_json[0]['earthquake']['hypocenter']['name']
    magnitude = data_json[0]['earthquake']['hypocenter']['magnitude']
    time = data_json[0]['earthquake']['time']
    tsuname = data_json[0]['earthquake']['domesticTsunami']
    print(f"Hypocenter: {name}")
    print(f"Magnitude: {magnitude}")
    print(f"Time: {time}")
    if tsuname == 'None':
        print("Tsunami: No tsunami was triggered by the earthquake.")
    else:
        print(f"Tsunami: {tsuname}")

elif code == 552:
    areas = data_json[0]['areas']
    time = data_json[0]['issue']['time']
    print(f"Area: {areas}")
    print(f"Time: {time}")
else:
    print("Code is incorrect.")
