# !/usr/bin/env python3

import argparse
import config
import json
import requests
import sys

def set_params(code, limit):
    offset = 0
    return {"codes":code, "limit":limit, "offset":offset}

def get_info(url, params):
    results = requests.get(url, params=params)
    if results.status_code != 200:
        print("Failed to get the informatiln. Parameters are incorrect.")
        sys.exit(1)

    return results.json()

def show_info(data_json, code, limit):
    for i in range(limit):
        print(f"-----No.{i + 1}-----")
        if len(data_json) < i + 1:
            print("No data")
            continue

        if code == 551:
            quake = data_json[i]
            id = quake['id']
            name = quake['earthquake']['hypocenter']['name']
            magnitude = quake['earthquake']['hypocenter']['magnitude']
            time = quake['earthquake']['time']
            tsuname = quake['earthquake']['domesticTsunami']
            print(f"ID: {id}")
            print(f"Hypocenter: {name}")
            print(f"Magnitude: {magnitude}")
            print(f"Time: {time}")
            if tsuname == 'None':
                print("Tsunami: No tsunami was triggered by the earthquake.")
            else:
                print(f"Tsunami: {tsuname}")

        elif code == 552:
            tsunami = data_json[i]
            id = tsunami['id']
            areas = [area['name'] for area in tsunami['areas']]
            areas_string = ','.join(areas)
            time = tsunami['issue']['time']
            print(f"ID: {id}")
            print(f"Areas: {areas_string}")
            print(f"Time: {time}")

        else:
            print("Code is incorrect.")
            sys.exit(1)

if __name__ == "__main__":
    url = config.URL
    parser = argparse.ArgumentParser(description="Show earthquake information")
    parser.add_argument("--code", type=int, default=551, help="Set 551(earthquake) or 552(tsunami). (default: 551)")
    parser.add_argument("--limit", type=int, default=1, help="Set the number of information. (default: 1)")
    args = parser.parse_args()

    params = set_params(args.code, args.limit)
    info = get_info(url, params)
    show_info(info, args.code, args.limit)

