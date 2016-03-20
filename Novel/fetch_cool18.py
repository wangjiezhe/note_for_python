#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
from bs4 import BeautifulSoup

BASEURL = 'http://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid='
ENCODING = 'gb18030'
GOAGENT = {'http': '127.0.0.1:8087'}
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36'}


def refine(text):
    text = text.replace('www.6park.com', '\n')
    return text


def get(url):
    req = requests.get(url, headers=HEADERS, proxies=GOAGENT)
    if req.ok:
        source = BeautifulSoup(req.content, from_encoding=ENCODING,
                               features="lxml")
        title = source.title.text
        content = source.pre.text
        # content = '\n'.join([line.text for line in source.pre.find_all('p')])
        text = refine(content)
        return title, text


def main():
    tids = sys.argv[1:]
    print(tids)
    if len(tids) == 0:
        print('No specific tid!')
        sys.exit(1)
    for tid in tids:
        url = BASEURL + tid
        title, text = get(url)
        print(title)
        filename = title + '.txt'
        with open(filename, 'w') as fp:
            fp.write(text)


if __name__ == '__main__':
    main()
