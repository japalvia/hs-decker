#!/bin/env python

# Read Hearthstone card name and try to return corresponding JSON encoded object
# and serialize it to JSON formatted str to stdout.

import json
import sys

def main():
    name = sys.argv[1]
    cards = sys.argv[2]

    with open(cards) as f:
        data = json.load(f)
        for d in data:
            if d['name'] == name:
                json.dump(d, sys.stdout)
                return

        sys.exit("Card not found")

if __name__ == "__main__":
    main()
