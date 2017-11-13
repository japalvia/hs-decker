#!/bin/env python

# Add Hearthstone card as JSON object to the given collection.

import json
import os
import sys

COLLECTIBLE = 'data/cards.collectible.json'
MYCOLLECTION = 'data/mycollection.json'

def usage():
    print("Usage: {} <card name> <count>".format(sys.argv[0]), file=sys.stderr)

def bad_usage(msg):
    usage()
    sys.exit(msg)

def query_card(name):
    with open(COLLECTIBLE) as f:
        cards = json.load(f)
        for c in cards:
            if c['name'] == name:
                return c
    return None

def main():

    if len(sys.argv) != 3:
        bad_usage("Incorrect number of arguments")

    name = sys.argv[1]
    count = int(sys.argv[2])

    if len(name) == 0:
        bad_usage("Card name is empty string")
    if count != 1 and count != 2:
        bad_usage("Card count must be 1 or 2")

    card = query_card(name)
    if not card:
        sys.exit("Card not found: {}".format(name))
    card['count'] = count

    mycards = None
    try:
        f = open(MYCOLLECTION, "r")
        mycards = json.load(f)
    except FileNotFoundError:
        mycards = json.loads('[]')

    found = False
    for c in mycards:
        if c['name'] == name:
            found = True
            if c['count'] == 1:
                c['count'] = 2
            elif c['count'] == 2:
                print("Already in collection: {} (2)".format(c['name']))
                return
            else:
                sys.exit("Card {} count is unexpected: {}"
                      .format(c['name'], c['count']))
            break

    with open(MYCOLLECTION, 'w') as out:
        if not found:
            mycards.append(card)
        out.write(json.dumps(mycards))

if __name__ == "__main__":
    main()
