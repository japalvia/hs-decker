#!/bin/env python

# Read Hearthstone card name and try to return corresponding JSON object

import json
import sys

def main():
    name = sys.argv[1]
    cards = sys.argv[2]

    with open(cards) as f:
        data = json.load(f)
        for d in data:
            if d['name'] == name:
                print(json.dumps(d))
                break

        sys.exit("Card not found")

if __name__ == "__main__":
    main()
