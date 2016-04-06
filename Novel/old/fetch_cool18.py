#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import os.path
import requests
from itertools import count
from bs4 import BeautifulSoup

BASEURL = 'http://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=%s'
ENCODING = 'gb18030'
GOAGENT = {'http': '127.0.0.1:8087'}
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36'}


def refine(text):
    # text = text.replace('<br /> <br />', '\n')
    # text = text.replace('<br />', '\n')
    # text = re.sub('<.*bodyend.*>.*', '', text)
    text = text.replace('www.6park.com', '\n')
    text = text.replace('\r\n', '\n')
    return text


def get(url):
    req = requests.get(url, headers=HEADERS, proxies=GOAGENT)
    if req.ok:
        source = BeautifulSoup(req.content, from_encoding=ENCODING,
                               features="lxml")
        title = source.title.text
        content = source.pre.text
        # content = '\n'.join([line.text for line in source.pre.find_all('p')])
        # content = str(source.pre)
        text = refine(content)
        return title, text


def make_filename(title):
    filename = '%s.txt' % title
    if os.path.exists(filename):
        for i in count(1):
            filename = '%s(%d).txt' % (title, i)
            if not os.path.exists(filename):
                break
    return filename


def download(tid):
    url = BASEURL % tid
    try:
        title, text = get(url)
        print('%s : %s' % (tid, title))
    except AttributeError:
        print('%s : No such page!' % tid)
        return
    filename = make_filename(title)
    with open(filename, 'w') as fp:
        fp.write(text)


def main():
    tids = sys.argv[1:]
    print(tids)
    if len(tids) == 0:
        print('No specific tid!')
        sys.exit(1)
    for tid in tids:
        download(tid)


if __name__ == '__main__':
    main()
