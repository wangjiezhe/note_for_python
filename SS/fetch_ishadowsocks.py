#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
from pyquery import PyQuery as pq

GOAGENT = {'http': '127.0.0.1:8087'}
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'
}
URL = 'http://www.ishadowsocks.net/'
CONF = '/etc/shadowsocks/iss-%s.json'


class Iss(object):

    def __init__(self, url, headers=None, proxies=None):
        self.url = url
        self.headers = headers or {}
        self.proxies = proxies or {}
        self.doc = pq(url, headers=self.headers, proxies=self.proxies)
        self.accounts_name = ['us', 'hk', 'jp']
        self.conf_name = ['server', 'server_port', 'password', 'method']
        self.accounts = self._parse()

    @staticmethod
    def _value(text):
        pattern = re.match(r'\S+:\s*(\S+)', text)
        return pattern.group(1)

    def _get_account(self, accounts, ind):
        acc = accounts.eq(ind)
        status = self._value(acc.children().eq(len(self.conf_name)).text())
        if status == '正常':
            res = {k: self._value(acc.children().eq(v).text())
                   for v, k in enumerate(self.conf_name)}
            return res

    def _parse(self):
        accounts = self.doc('#free')('.col-lg-4')
        res = [{k: self._get_account(accounts, v)}
               for v, k in enumerate(self.accounts_name)]
        return res

    def dump(self):
        for ac in self.accounts:
            for k, v in ac.items():
                if v is not None:
                    with open(CONF % k, 'w') as fp:
                        json.dump(v, fp, indent=2)


def main():
    iss = Iss(URL, HEADERS, GOAGENT)
    iss.dump()


if __name__ == '__main__':
    main()
