#!/bin/env python

# Add Hearthstone card as JSON object to the given collection.

import json
import os
import sys

def main():
    mycards_file = sys.argv[1]

    input_str = sys.stdin.buffer.read()

    card = json.loads(input_str)

    mycards = None

    try:
        f = open(mycards_file, "r")
        mycards = json.load(f)
    except FileNotFoundError:
        mycards = json.loads('[]')

    for c in mycards:
        if c['name'] == card['name']:
            print("already in collection: {}".format(card['name']))
            return

    with open(mycards_file, 'w') as out:
        mycards.append(card)
        out.write(json.dumps(mycards))

if __name__ == "__main__":
    main()
