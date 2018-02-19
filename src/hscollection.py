#!/bin/env python3

import argparse
import binascii
import json
import sys

from hearthstone.deckstrings import Deck
from hearthstone.enums import FormatType, Rarity, CardSet

class HSCollection:
    def __init__(self, collectible_path, mycollection_path):
        self.mycollection_path = mycollection_path
        self.mycollection = None
        self.cards_collectible = None

        self.load_collectible(collectible_path)
        self.load_mycollection(mycollection_path)

    def error(self, message):
        sys.exit('ERROR:' + message)

    def load_collectible(self, collectible):
        with open(collectible) as f:
            self.cards_collectible = json.load(f)

    def card_by_name(self, name):
        for c in self.cards_collectible:
            if c['name'] == name:
                return c
        return None

    def collectible_by_Id(self, dbfId):
        for c in self.cards_collectible:
            if c['dbfId'] == dbfId:
                return c
        return None

    def load_mycollection(self, collection):
        try:
            f = open(collection)
            self.mycollection = json.load(f)
        except FileNotFoundError:
            print('Initializing empty collection')
            self.mycollection = json.loads('[]')

    def add_card(self, name, count):
        count = int(count)
        if count != 1 and count != 2:
            self.error('Card count ({}) must be (1) or (2)'.format(count))

        card = self.card_by_name(name)
        if not card:
            self.error('Card not found: {}'.format(name))
        card['count'] = count

        new_card = True
        for c in self.mycollection:
            if c['name'] == name:
                new_card = False
                if c['count'] == 1:
                    c['count'] = 2
                elif c['count'] == 2:
                    print('Already in collection: {} (2)'.format(c['name']))
                    return
                else:
                    self.error('Card {} count is unexpected: {}'
                          .format(c['name'], c['count']))
                break
        if new_card:
           self.mycollection.append(card)

    def save(self):
        with open(self.mycollection_path, 'w') as f:
            f.write(json.dumps(self.mycollection))

    def add_from_file(self, path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('#', 1)
                if len(parts[0]) == 0: # line starts with comment
                    continue
                data = parts[0].split(' ', 1)
                self.add_card(data[1].strip(), data[0])
                # Ignoring comment in parts[1]

    def crafting_cost(self, card, count):
        cost = Rarity[card['rarity']].crafting_costs[0]
        return cost * count

    '''Translate CardSet enums to human readable set names.
       Contains only Standard sets.
       Does not translate _RESERVE enums since I don't know what they contain
       and there are no cards in those sets (in cards.collectible.json).'''
    def readable_card_set(self, card_set):
        switcher = {
                CardSet.CORE.name : 'Basic',
                CardSet.EXPERT1.name : 'Classic',
                CardSet.OG.name : 'Whispers of the Old Gods',
                CardSet.KARA.name : 'One Night in Karazhan',
                CardSet.GANGS.name : 'Mean Streets of Gadgetzan',
                CardSet.UNGORO.name : 'Journey to Un\'Goro',
                CardSet.ICECROWN.name : 'Knights of the Frozen Throne',
                CardSet.LOOTAPALOOZA.name : 'Kobolds and Catacombs',
        }
        return switcher.get(card_set, 'Not found:' + card_set)

    '''Return a list of tuplets (card, found, missing)'''
    def load_deckstring(self, deckstring):
        cards = []

        try:
            deck = Deck.from_deckstring(deckstring)
        except binascii.Error:
            print('Deck string is invalid base64 string: {}'.format(deckstring))
            return None

        total_cost = 0
        for (dbfId, count) in deck.cards:
            count = int(count)
            found = False
            for card in self.mycollection:
                if card['dbfId'] == dbfId:
                    found = True
                    if card['count'] >= count:
                        cards.append((card, count, 0))
                    else:
                        missing = count - card['count']
                        cards.append((card, card['count'], missing))
            card = None
            if not found:
                card = self.collectible_by_Id(dbfId)
                cards.append((card, 0, count))

        return cards

    def show_deck(self, deckstring):
        cards_tuple = self.load_deckstring(deckstring)
        if not cards_tuple:
            return

        total_cost = 0
        print("\n### Checking cards in my collection ###\n")
        for ct in cards_tuple:
            card = ct[0]
            found = ct[1]
            missing = ct[2]
            sys.stdout.write('{} {}'.format(found + missing,
                             card['name'].ljust(27, '.')))
            if missing:
                cost = self.crafting_cost(card, missing)
                total_cost += cost
                print("missing ({}): {} dust ({})".
                      format(missing, cost,
                             self.readable_card_set(card['set'])))
            else:
                print("OK")

        print("\n### Requires {} dust ###\n".format(total_cost))

    def add_card_set(self, setname):
        print('NOT IMPLEMENTED')


def usage():
    print('select one operation:\n'
          '\t--deck (load a deck string)\n'
          '\t--list (add cards from a file list\n'
          '\t--set (add all cards in expansion\n'
          '\t--card --count (add this card count times)', file=sys.stderr)

def bad_usage(msg):
    usage()
    sys.exit('ERROR: {}'.format(msg))

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Manage Hearthstone cards collection')
    parser.add_argument('-c', '--collectible', help='cards.collectible.json')
    parser.add_argument('-m', '--mycollection', help='mycollection.json')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--deck', help='deck string')
    group.add_argument('--list', help='cards to add listed in a file')
    group.add_argument('--set', help='add all cards in expansion set')
    group.add_argument('--card', help='add card by name')
    parser.add_argument('--count', help='card count: 1 or 2')

    args = parser.parse_args()

    collection = HSCollection(args.collectible, args.mycollection)

    # Operations for constructing a deck with deck string from collection.
    if args.deck:
        collection.show_deck(args.deck)
        sys.exit(0)

    # Operations for adding cards to mycollection.
    if (args.card and not args.count) or (not args.card and args.count):
        bad_usage('--card and --count must be used together')
    if args.card:
        collection.add_card(args.card, args.count)
    if args.list:
        collection.add_from_file(args.list)
    elif args.set:
        collection.add_card_set(args.set)
    else:
        bad_usage('Operation missing')
    collection.save()

