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


def refine(text):
    text = text.replace('\r\n', '\n')
    return text


def get(topic_id):
    title = ''
    content_list = []
    topic_url = BASE_URL % topic_id
    comments_url = COMMENTS_URL % topic_id

    req = requests.get(topic_url, headers=HEADERS)
    ret = req.json()
    author_id = ret['author']['id']
    num_comments = ret['comments_count']
    title = ret['title']
    content_list.append(refine(ret['content']))

    for i in range(num_comments // PER_PAGE_COUNT + 1):
        params = {
            'start': i * PER_PAGE_COUNT,
            'count': PER_PAGE_COUNT
        }
        req = requests.get(comments_url, headers=HEADERS, params=params)
        ret = req.json()
        for c in ret['comments']:
            if c['author']['id'] != author_id:
                continue
            content_list.append(refine(c['text']))

    content = '\n\n\n\n'.join(content_list)
    return title, content


def download(topic_id):
    title, content = get(topic_id)
    print(title)
    filename = title + '.txt'
    filename = filename.replace('/', '_')
    with open(filename, 'w') as fp:
        fp.write(content)


def main():
    topic_ids = sys.argv[1:]
    if len(topic_ids) == 0:
        print('No specific topic id!')
        sys.exit(1)
    print(topic_ids)
    for topic_id in topic_ids:
        download(topic_id)


if __name__ == '__main__':
    main()
