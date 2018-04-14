#!/bin/env python3

import argparse
import binascii
import json
import os
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
        sys.exit('ERROR: ' + message)

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

    def reset(self):
        self.mycollection = json.loads('[]')

    def remove_card(self, name, count=1):
        count = int(count)
        if count != 1 and count != 2:
            self.error('Card count ({}) must be (1) or (2)'.format(count))
        if not self.mycollection:
            self.error('Failed to remove \'{}\' from an empty collection.'.
                       format(name))

        for i, c in enumerate(self.mycollection):
            if c['name'] == name:
                if c['count'] > count:
                    c['count'] = c['count'] - count
                elif c['count'] == count:
                    del self.mycollection[i]
                else:
                    self.error('Failed to remove count ({}) \'{}\'.'
                               'Collection has count ({})'.format(
                               count, name, c['count']))
                return

            self.error('Failed to remove \'{}\': card not found'.format(name))

    def add_card(self, name, count=1):
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
    @staticmethod
    def readable_card_set(card_set):
        switcher = {
                CardSet.CORE.name : 'Basic',
                CardSet.EXPERT1.name : 'Classic',
                CardSet.OG.name : 'Whispers of the Old Gods',
                CardSet.KARA.name : 'One Night in Karazhan',
                CardSet.GANGS.name : 'Mean Streets of Gadgetzan',
                CardSet.UNGORO.name : 'Journey to Un\'Goro',
                CardSet.ICECROWN.name : 'Knights of the Frozen Throne',
                CardSet.LOOTAPALOOZA.name : 'Kobolds and Catacombs',
                CardSet.GILNEAS.name : 'Witchwood',
        }
        return switcher.get(card_set, 'Not found:' + card_set)

    '''Return a list of tuplets (card, found, missing)
       where the type is (dict, int, int) --> (JSON card object, count, count)
       Invalid cards are filled with minimal data and have 0 total count.'''
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
                if not card:
                    card = { 'name': 'INVALID DBFID ({})'.format(dbfId) }
                    count = 0
                cards.append((card, 0, count))

        return cards

    def show_deck(self, deckstring):
        cards_tuple = self.load_deckstring(deckstring)
        if not cards_tuple:
            return

        total_cost = 0
        print('\n### Checking cards in my collection ###\n')
        for ct in cards_tuple:
            card = ct[0]
            found = ct[1]
            missing = ct[2]
            count = found + missing

            sys.stdout.write('{} {}'.format(count,
                             card['name'].ljust(27, '.')))
            if count != 1 and count != 2:
                print('FAIL')
            elif missing:
                cost = self.crafting_cost(card, missing)
                total_cost += cost
                print('missing ({}): {} dust ({})'.
                      format(missing, cost,
                             self.readable_card_set(card['set'])))
            else:
                print('OK')

        if count == 1 or count == 2:
            print('\n### Requires {} dust ###\n'.format(total_cost))
        else:
            print('\n### Broken deck. Valid cards require {} dust ###\n'
                  .format(total_cost))

    def add_card_set(self, setnumber):
        e = None
        try:
            e = CardSet(int(setnumber))
        except ValueError:
            bad_usage('Invalid set number: {}'.format(setnumber))

        n = e.name
        for c in self.cards_collectible:
            if c['set'] == n:
                self.add_card(c['name'], 2)

def usage_card_sets():
    usage = ''
    for s in CardSet:
        if s.is_standard:
             usage = '{}{}{}{}'.format(usage, str(s.value).ljust(7, '.'),
                                       HSCollection.readable_card_set(s.name),
                                       os.linesep)
    return usage

def cardset_enums():
    enums = []
    for s in CardSet:
        if s.is_standard:
            enums.append(s.value)
    return enums

def bad_usage(msg):
    sys.exit('ERROR: {}'.format(msg))

def opts_add_cards(collection, args):
    if  args.card:
        for c in args.card:
            collection.add_card(c)
    if args.set:
        for s in args.set:
            collection.add_card_set(s)
    if args.list:
        for l in args.list:
            collection.add_from_file(l)

def opts_rem_cards(collection, args):
    if isinstance(args.rem_card, str):
        collection.remove_card(args.rem_card)
    elif isinstance(args.rem_card, list):
        for c in args.rem_card:
            collection.remove_card(c)

def opts_show_deck(collection, args):
    if args.deck:
        collection.show_deck(args.deck)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('hscollection')
    parser.add_argument('-c', '--collectible', help='cards.collectible.json')
    parser.add_argument('-m', '--mycollection', help='mycollection.json')
    parser.add_argument('-r', '--reset', action='store_true',
                        help='reset your collection')
    subparsers = parser.add_subparsers()

    addparser = subparsers.add_parser('add',
                                       help='add cards to your collection',
                                       formatter_class=argparse.RawTextHelpFormatter)
    addparser.add_argument('-c', '--card', action='append', help='card name')
    addparser.add_argument('-l', '--list', action='append', help='file path')
    addparser.add_argument('-s', '--set', action='append', type=int,
                           choices=cardset_enums(),
                           help=usage_card_sets())
    addparser.set_defaults(func=opts_add_cards)

    remparser = subparsers.add_parser('remove',
                                      help='remove cards from your collection')
    remparser.add_argument('rem_card', help='card name')
    remparser.set_defaults(func=opts_rem_cards)

    deckparser = subparsers.add_parser('deck',
                                       help='display a deck using your collection')
    deckparser.add_argument('deck', help='deck string')
    deckparser.set_defaults(func=opts_show_deck)

    args = parser.parse_args()

    collection = HSCollection(args.collectible, args.mycollection)
    if args.reset:
        collection.reset()

    # Handle subcommand
    args.func(collection, args)

    collection.save()

