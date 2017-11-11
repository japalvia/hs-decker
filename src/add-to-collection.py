#!/bin/env python

# Add Hearthstone card as JSON object to the given collection.

import json
import sys

def main():
    obj_str = sys.argv[1]
    collection = sys.argv[2]

    obj = json.loads(obj_str)

    print("obj: {}".format(obj))

if __name__ == "__main__":
    main()
