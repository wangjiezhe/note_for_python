#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re

from time import sleep
from pyquery import PyQuery as pq
from urllib.error import HTTPError

BASE_URL = 'http://www.123yq.org/read/%s/%s/'
INTRO_URL = 'http://www.123yq.org/xiaoshuo_%s.html'
GOAGENT = {'http': '127.0.0.1:8087'}
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36'}
ENCODING = 'GB18030'


class Yq123(object):

    def __init__(self, tid, headers=None, proxies=None):
        self.tid = str(tid)
        self.url = BASE_URL % (self.tid[:-3], self.tid)
        self.encoding = ENCODING
        self.headers = headers or {}
        self.proxies = proxies or {}
        self.tool = Tool()
        self.doc = pq(self.url, headers=self.headers, proxies=self.proxies,
                      encoding=self.encoding)
        self.title, self.author = self.get_title_and_author()

    def get_title_and_author(self):
        st = self.doc('meta').filter(
            lambda i, e: pq(e).attr['name'] == 'keywords').attr['content']
        return re.match(r'(.*?),(.*?),', st).groups()

    @property
    def chapter_list(self):
        clist = self.doc('dd').map(
            lambda i, e: (pq(e)('a').attr['href'], pq(e).text())
        ).filter(
            lambda i, e: e[0] is not None
        )
        clist.sort(key=lambda s: int(re.match('.*/(\d*)\.shtml', s[0]).group(1)))
        return clist

    def get_intro(self):
        intro_url = INTRO_URL % self.tid
        intro_page = pq(intro_url, headers=self.headers, proxies=self.proxies,
                        encoding=self.encoding)
        intro = intro_page('.intro').html()
        intro = self.tool.replace(intro)
        return intro

    @property
    def download_dir(self):
        return os.path.join(os.getcwd(), "《%s》%s" % (self.title, self.author))

    def dump_split(self):
        if not os.path.isdir(self.download_dir):
            os.makedirs(self.download_dir)
        print('《%s》%s' % (self.title, self.author))
        for i, s in enumerate(self.chapter_list):
            self.dump_chapter(s[0], s[1], i+1)

    def dump_chapter(self, url, title, num):
        try:
            page = Yq123Page(url, title, self.headers, self.proxies)
            page.dump(folder=self.download_dir, num=num)
        except HTTPError:
            print("Wait 5s to retry...")
            sleep(5)
            self.dump_chapter(url=url, title=title, num=num)

    def dump(self):
        name = '《%s》%s.txt' % (self.title, self.author)
        print(name)
        path = os.path.join(os.getcwd(), name)
        with open(path, 'w') as fp:
            fp.write(self.title)
            fp.write('\n\n')
            fp.write(self.author)
            fp.write('\n\n\n')
            fp.write(self.get_intro())
            for i, s in enumerate(self.chapter_list):
                content = self.get_chapter(s[0], s[1])
                fp.write('\n\n\n\n')
                print(s[1])
                fp.write(s[1])
                fp.write('\n\n\n')
                fp.write(content)

    def get_chapter(self, url, title):
        try:
            page = Yq123Page(url, title, self.headers, self.proxies)
            return page.get_content()
        except HTTPError:
            print("Wait 5s to retry...")
            sleep(5)
            return self.get_chapter(url, title)


class Yq123Page(object):

    def __init__(self, url, title, headers=None, proxies=None):
        self.url = url
        self.title = title
        self.encoding = ENCODING
        self.headers = headers or {}
        self.proxies = proxies or {}
        self.tool = Tool()

        self.doc = pq(self.url, headers=self.headers, proxies=self.proxies,
                      encoding=self.encoding)

    def get_content(self):
        content = self.doc('#TXT').html()
        content = self.tool.replace(content)
        return content

    def dump(self, path=None, folder=None, num=None):
        if path is None:
            if num is not None:
                pre = '「%d」' % num
            else:
                pre = ''
            name = '%s%s.txt' % (pre, self.title)
            if folder is None:
                path = os.path.join(os.getcwd(), name)
            else:
                path = os.path.join(folder, name)
        print(self.title)
        with open(path, 'w') as fp:
            fp.write(self.title)
            fp.write('\n\n\n')
            fp.write(self.get_content())


class Tool(object):

    def __init__(self):
        self._remove_addr = re.compile(r'<a.*?>.*?</a>')
        self._remove_div = re.compile(r'<div.*?>.*?</div>')
        self._replace_br = re.compile(r'<br\s*/\s*>')
        self._replace_xa = re.compile(r'\xa0')
        self._remove_r = re.compile(r'&#13;|\r')
        self._remove_ot = re.compile(r'<.*?>')

    def replace(self, text):
        text = re.sub(self._remove_addr, '', text)
        text = re.sub(self._remove_div, '', text)
        text = re.sub(self._replace_br, '\n', text)
        text = re.sub(self._replace_xa, ' ', text)
        text = re.sub(self._remove_r, '', text)
        text = re.sub(self._remove_ot, '', text)
        return text.strip()


def main():
    tids = sys.argv[1:]
    print(tids)
    if len(tids) == 0:
        print('No specific tid!')
        sys.exit(1)
    for tid in tids:
        yq = Yq123(tid, HEADERS, GOAGENT)
        yq.dump()


if __name__ == '__main__':
    main()
