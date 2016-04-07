#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import os.path
from itertools import count
from pyquery import PyQuery as pq

BASEURL = 'http://www.cool18.com/bbs4/index.php?app=forum&act=threadview&tid=%s'
GOAGENT = {'http': '127.0.0.1:8087'}
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36'}


class Tool(object):

    def __init__(self):
        self.remove_addr = re.compile(r'<a.*?>|</a>')  # remove hyperlink
        # replace line break tag with '\n'
        # self.replace_line = re.compile(r'</p>')
        # replace paragraph tag with '\n' and two full width blank
        self.replace_para = re.compile(r'<p.*?>')
        # replace line break with '\n'
        self.replace_br = re.compile(r'<br\s*/*>')
        self.remove_r = re.compile(r'&#13;|\r')  # remove '\r'
        self.remove_ad = re.compile(r'www\.6park\.com')
        # remove needless content at the end
        self.remove_end = re.compile(r'<.*?bodyend.*?>.*')
        self.remove_ot = re.compile(r'<.*?>')  # remove all other tags

    def replace(self, text):
        text = re.sub(self.remove_addr, '', text)
        # text = re.sub(self.replace_line, '\n', text)
        text = re.sub(self.replace_para, '\n\n', text)
        text = re.sub(self.replace_br, '\n', text)
        text = re.sub(self.remove_r, '', text)
        text = re.sub(self.remove_ad, '', text)
        text = re.sub(self.remove_end, '', text)
        text = re.sub(self.remove_ot, '', text)
        return text.strip()


class Cool18(object):

    def __init__(self, tid, headers=None, proxies=None):
        self.baseurl = BASEURL
        self.tid = tid
        self.url = self.baseurl % tid
        self.headers = headers or {}
        self.proxies = proxies or {}
        self.tool = Tool()
        self.doc = pq(self.url, headers=self.headers, proxies=self.proxies)
        self.title = self._get_title()

    def _get_title(self):
        return self.doc('title').text()

    def get_content(self):
        pre = self.doc('pre').html()
        return self.tool.replace(pre)

    def dump(self):
        if self.title == '':
            print('%s : No such page!' % self.tid)
            return
        filename = self._get_filename()
        content = self.get_content()
        print('%s : %s' % (self.tid, filename))
        with open(filename, 'w') as fp:
            fp.write(content)

    def _get_filename(self):
        filename = '%s.txt' % self.title
        if os.path.exists(filename):
            for i in count(1):
                filename = '%s(%d).txt' % (self.title, i)
                if not os.path.exists(filename):
                    break
        return filename


def main():
    tids = sys.argv[1:]
    print(tids)
    if len(tids) == 0:
        print('No specific tid!')
        sys.exit(1)
    for tid in tids:
        coo = Cool18(tid, HEADERS, GOAGENT)
        coo.dump()


if __name__ == '__main__':
    main()
