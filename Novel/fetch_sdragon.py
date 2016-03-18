#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
from bs4 import BeautifulSoup

BASEURL = 'http://ebook.s-dragon.org/forum/archiver/?tid-'
ENCODING = 'Big5'
GOAGENT = {'http': '127.0.0.1:8087'}
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36'}


def get(url):
    req = requests.get(url, headers=HEADERS, proxies=GOAGENT)
    if req.ok:
        source = BeautifulSoup(req.content, from_encoding=ENCODING,
                               features="lxml")
        title = source.title.text
        content = '\n'.join(
            [k.text for k in source.find_all(
                'div', attrs={'class': 'archiver_post'})])
        return title, content


def main():
    tids = sys.argv[1:]
    print(tids)
    if len(tids) == 0:
        print('No specific tid!')
        return -1
    for tid in tids:
        url = BASEURL + tid
        title, text = get(url)
        print(title)
        filename = title + '.txt'
        with open(filename, 'w') as fp:
            fp.write(text)


if __name__ == '__main__':
    main()
