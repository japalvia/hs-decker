#!/bin/env python

import subprocess
import sys

CMD = './src/add-to-collection.py'

def main():
    cardlist = sys.argv[1]

    with open(cardlist) as f:
        for line in f:
            if line.startswith('#'):
                continue
            arr = line.split(' ', 1)
            count = arr[0]
            card = arr[1].strip()
            subprocess.run([CMD, card, count], stdout=True, stderr=True, check=True)

if __name__ == "__main__":
    main()
