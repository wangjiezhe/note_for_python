#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests

BASE_URL = 'https://api.douban.com/v2/group/topic/%s/'  # id
COMMENTS_URL = BASE_URL + 'comments'
PER_PAGE_COUNT = 100

HEADERS = {
    'Host': 'api.douban.com',
    "Referer": 'api.douban.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36'
}


class DoubanGroup(object):

    def __init__(self, topic_id):
        self.topic_url = BASE_URL % topic_id
        self.comments_url = COMMENTS_URL % topic_id
        self.req = requests.get(self.topic_url, headers=HEADERS).json()

    @property
    def title(self):
        return self.req['title']

    @property
    def author_id(self):
        return self.req['author']['id']

    @property
    def num_comments(self):
        return self.req['comments_count']

    @staticmethod
    def refine(text):
        text = text.replace('\r\n', '\n')
        return text

    def get_content(self):
        content_list = [self.refine(self.req['content'])]

        for i in range(self.num_comments // PER_PAGE_COUNT + 1):
            params = {
                'start': i * PER_PAGE_COUNT,
                'count': PER_PAGE_COUNT
            }
            req = requests.get(self.comments_url, headers=HEADERS, params=params).json()
            for c in req['comments']:
                if c['author']['id'] != self.author_id:
                    continue
                content_list.append(self.refine(c['text']))

        content = '\n\n\n\n'.join(content_list)
        return content

    def dump(self):
        print(self.title)
        filename = self.title + '.txt'
        filename = filename.replace('/', '_')
        with open(filename, 'w') as fp:
            fp.write(self.get_content())


def main():
    topic_ids = sys.argv[1:]
    if len(topic_ids) == 0:
        print('No specific topic id!')
        sys.exit(1)
    print(topic_ids)
    for topic_id in topic_ids:
        dbg = DoubanGroup(topic_id)
        dbg.dump()


if __name__ == '__main__':
    main()
