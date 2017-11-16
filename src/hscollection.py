#!/bin/env python

import argparse
import json
import sys

class HSCollection:
    def __init__(self, collectible_path, mycollection_path):
        self.mycollection_path = mycollection_path
        self.mycollection = None # = 'data/mycollection.json'
        self.cards_collectible = None # = 'data/cards.collectible.json'

        self.load_collectible(collectible_path)
        self.load_mycollection(mycollection_path)

    def error(self, message):
        sys.exit(message)

    def load_collectible(self, collectible):
        with open(collectible) as f:
            self.cards_collectible = json.load(f)

    def card2json(name):
        for c in self.cards_collectible:
            if c['name'] == name:
                return c
        return None

    def load_mycollection(self, collection):
        try:
            f = open(collection)
            self.mycollection = json.load(f)
        except FileNotFoundError:
            print("Initializing empty collection")
            self.mycollection = json.loads('[]')

    def add_card(name, count):
        if count != 1 and count != 2:
            self.error("Card count ({}) must be 1 or 2".format(count))

        card = card2json(name)
        if not card:
            self.error("Card not found: {}".format(name))
        card['count'] = count

        new_card = True
        for c in self.mycollection:
            if c['name'] == name:
                new_card = False
                if c['count'] == 1:
                    c['count'] = 2
                elif c['count'] == 2:
                    print("Already in collection: {} (2)".format(c['name']))
                    return
                else:
                    self.error("Card {} count is unexpected: {}"
                          .format(c['name'], c['count']))
                break
        if new_card:
           self.mycollection.append(card)

    def save_mycollection(self):
        with open(self.mycollection_path, 'w') as f:
            f.write(json.dumps(self.mycollection))

    def add_from_file(path):
        pass

def usage():
    print("Usage: {} <card name> <count>".format(sys.argv[0]), file=sys.stderr)

def bad_usage(msg):
    usage()
    sys.exit(msg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser('Manage Hearthstone cards collection')
    parser.add_argument('-c', '--collectible', help='cards.collectible.json')
    parser.add_argument('-m', '--mycollection', help='mycollection.json')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--list', help='cards to add listed in a file')
    group.add_argument('--card', help='card name')

    parser.add_argument('--count', help='card count: 1 or 2')

    args = parser.parse_args()
    if (args.card and not args.count) or (not args.card and argc.count):
        bad_usage("--card and --count must be used together")

    collection = HSCollection(args.collectible, args.mycollection)


