#!/bin/env python3

import urllib.request
import shutil

url = 'https://api.hearthstonejson.com/v1/latest/enUS/cards.collectible.json'
filename = 'data/cards.collectible.json'

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
response = urllib.request.urlopen(req)
with open(filename, 'wb') as f:
    shutil.copyfileobj(response, f)
