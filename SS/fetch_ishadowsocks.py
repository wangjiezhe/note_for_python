#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import argparse
from collections import OrderedDict

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
        self.accounts_name = ('us', 'hk', 'jp')
        self.conf_name = ('server', 'server_port', 'password', 'method')
        self.accounts = self.parse()

    @staticmethod
    def _value(text):
        pattern = re.match(r'\S+:\s*(\S*)', text)
        return pattern.group(1)

    def _get_account(self, accounts, ind):
        acc = accounts.eq(ind)
        status = self._value(acc.children().eq(len(self.conf_name)).text())
        if status == '正常':
            res = OrderedDict(
                (k, self._value(acc.children().eq(v).text()))
                for v, k in enumerate(self.conf_name))
            return res

    def parse(self):
        accounts = self.doc('#free')('.col-lg-4')
        res = {k: self._get_account(accounts, v)
               for v, k in enumerate(self.accounts_name)}
        return res

    def dump(self):
        for k, v in self.accounts.items():
            if v is not None:
                if v['password'] == '':
                    print('Warning: No password for %s!' % k)
                with open(CONF % k, 'w') as fp:
                    json.dump(v, fp, indent=2)

    def show(self):
        accounts = self.accounts
        for k, v in accounts.copy().items():
            if v is not None:
                if v['password'] == '':
                    del accounts[k]
        print(json.dumps(accounts, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description='Get free shadowsocks accounts from http://www.ishadowsocks.net/'
    )
    parser.add_argument('-n', '--no-proxy', action='store_true',
                        help='do not use proxy')
    args = parser.parse_args()
    if args.no_proxy:
        iss = Iss(URL, HEADERS)
    else:
        iss = Iss(URL, HEADERS, GOAGENT)
    iss.dump()
    iss.show()


if __name__ == '__main__':
    main()
