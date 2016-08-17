#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''\
将 kwplayer 下载的某个列表(默认为 Default)的歌曲拷入酷我音乐的音乐下载文件夹.
'''

import json
import sys
import os
import getopt
import shutil
import re

from textwrap import dedent

import pymtp
import mutagen.easyid3

FILENAME = "pls.json"
CACHE_DIR = os.path.expanduser("~/.cache/kuwo")
SONG_DIR = os.path.join(CACHE_DIR, "song")
# SONG_DIR = ("song")
# LRC_DIR = os.path.join(CACHE_DIR, "lrc")
MUSICFOLDER = 4


def usage():
    '''显示帮助'''
    help_text = '''\
            Usage: %s -o OUTDIR [JSONFILE]
            Options:
            -h --help   : display this help
            -o --outdir : set outfile directory
            --playlist  : set playlist to copy''' % sys.argv[0]
    print(dedent(help_text))


def analyse_args(args=sys.argv[1:]):
    '''解析命令行参数, 返回 json 文件, 目标文件夹及播放列表'''
    shortargs = "ho:"
    longargs = ["help", "outdir=", "playlist="]
    outdir = None
    playlist = None

    try:
        opts, jsonfiles = getopt.getopt(args, shortargs, longargs)
    except getopt.GetoptError:
        print("Getopt Error!")
        usage()
        sys.exit(1)

    if len(jsonfiles) > 0:
        jsonfile = jsonfiles[0]
    else:
        jsonfile = os.path.join(CACHE_DIR, FILENAME)

    for opt, value in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-o", "--outdir"):
            outdir = value
        elif opt == "--playlist":
            playlist = value

    if outdir is None:
        print("Option for outdir needed.")
        usage()
        sys.exit(1)

    if playlist is None:
        playlist = "Default"

    return jsonfile, outdir, playlist

# def generate_lrc_name(artist, song):
#     return artist + "-" + song + ".lrc"


def generate_origin_song_name(artist, song):
    '''生成原歌曲文件名'''
    return artist + "-" + song + ".mp3"


def generate_target_name(artist, song):
    '''生成目标文件名'''
    # 酷我音乐与 kwplayer 的歌曲命名方式相反.
    return song + "-" + artist + ".mp3"


def generate_dst_song_name(name):
    # 不能完全正确解析
    '''生成目标文件名'''
    # 酷我音乐与 kwplayer 的歌曲命名方式相反.
    pattern = r'(.+)-(.+)\.mp3'
    string = re.match(pattern, name)
    return string.expand(r'\2-\1.mp3')


def analyse(jsonobject, opt):
    '''从 json 文件中解析出某个播放列表的歌曲名'''
    song_list = []
    target_list = []
    # lrc_list = []

    if opt not in jsonobject.keys():
        print("Playlist %s does not exist." % opt)
        sys.exit(1)

    playlist = jsonobject[opt]

    for info in playlist:
        song_list.append(generate_origin_song_name(info[1], info[0]))
        target_list.append(generate_target_name(info[1], info[0]))
        # lrc_list.append(generate_lrc_name(info[1], info[0]))

    return list(zip(song_list, target_list))  # , lrc_list


def generate_lists(jsonobject):
    '''从 json 文件中解析出播放列表对应的序号代码'''
    list_dict = dict([item[:-1] for item in jsonobject['_names_']])
    playlist_names = ['Default', 'Music', '红楼梦', '此间的少年', '安与骑兵', '琵琶相']
    playlist_codes = [list_dict[item] for item in playlist_names]
    return playlist_codes


def copyfiles(file_and_dst_list, srcdir, outdir):
    '''将指定列表中的文件从原始文件夹复制到目标文件夹'''
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    for filename in file_and_dst_list:
        srcfile = os.path.join(srcdir, filename[0])
        # dstfile = os.path.join(outdir, generate_dst_song_name(filename))
        dstfile = filename[1]
        if (not os.path.exists(dstfile) or
            (os.path.exists(dstfile) and
             os.path.getsize(dstfile) != os.path.getsize(srcfile))):
            shutil.copy(srcfile, dstfile)


def cenc(name):
    """Check if it's not None and encode"""
    return name is not None and name.encode() or None


def cdec(name):
    """Check if it's not None and decode"""
    return name is not None and name.decode() or None


class MyMTP(pymtp.MTP):
    '''定制 MTP 类'''

    def sendfiles(self, file_and_dst_list, srcdir, parent=0):
        for name in file_and_dst_list:
            source = os.path.join(srcdir, name[0])
            # target = name
            # target = generate_dst_song_name(name)
            target = name[1]
            item_id = self.send_file_from_file(source, target, parent=parent)
            print(
                dedent("Create new file with\
                    ID: %s for File: %s" % (item_id, target)))

    def sendtrack(self, source, target, parent=0):
        '''将指定音轨文件通过 mtp 发送到目标文件夹, 自动获取 metadata'''
        easydata = mutagen.easyid3.Open(source)
        metadata = pymtp.LIBMTP_Track()

        if 'artist' in easydata:
            metadata.artist = cenc(easydata['artist'])
        if 'title' in easydata:
            metadata.title = cenc(easydata['title'])
        if 'album' in easydata:
            metadata.album = cenc(easydata['album'])
        if 'track' in easydata:
            metadata.tracknumber = easydata['track']

        track_id = self.send_track_from_file(
            source, target, metadata, parent=parent)

        print(
            dedent("Create new track with\
                ID: %s for Track: %s" % (track_id, target)))

        return track_id

    def sendtracks(self, tracklist, srcdir, parent=0):
        '''将指定播放列表中的音轨文件从原始文件夹通过 mtp 发送到目标文件夹'''
        for track in tracklist:
            source = os.path.join(srcdir, track[0])
            # target = generate_dst_song_name(track)
            target = track[1]
            self.sendtrack(source, target, parent=parent)


def main():
    '''主程序'''
    jsonfile, outdir, playlist = analyse_args()
    songlist = analyse(open(jsonfile), playlist)
    # songlist, lrclist = analyse(open(jsonfile), playlist)

    # 酷我音乐与 kwplayer 的文件夹命名不同.
    copyfiles(songlist, SONG_DIR, os.path.join(outdir, "music"))
    # copyfiles(lrclist, LRC_DIR, os.path.join(outdir, "lyrics"))


def main2():
    '''复制特定的几个播放列表, 忽略 --playlist 选项'''
    jsonfile = FILENAME
    outdir = analyse_args()[1]
    for playlist in generate_lists(open(jsonfile)):
        songlist = analyse(open(jsonfile), playlist)
        copyfiles(songlist, SONG_DIR, os.path.join(outdir, "music"))


def main3():
    '''通过 mtp 发送特定的几个播放列表的歌曲, 忽略 --playlist 选项'''
    jsonobject = json.load(open(FILENAME))
    lists = generate_lists(jsonobject)
    mtp = MyMTP()

    mtp.connect()
    print("Device Name : %s" % cdec(mtp.get_devicename()))

    for playlist in lists:
        track_and_target_list = analyse(jsonobject, playlist)
        # mtp.sendtracks(tracklist, SONG_DIR, parent=MUSICFOLDER)
        mtp.sendfiles(track_and_target_list, SONG_DIR, parent=MUSICFOLDER)

    print("Sending all tracks succeeded!")
    mtp.disconnect()


def test_mtp():
    '''mtp 测试程序'''
    mtp = MyMTP()
    mtp.connect()
    print("Device Name : %s" % cdec(mtp.get_devicename()))
    song_name = "Joe Hisaishi-天空之城(木吉他).mp3"
    source = os.path.join(SONG_DIR, song_name)
    target = generate_dst_song_name(song_name)
    mtp.sendtrack(source, target, parent=MUSICFOLDER)
    mtp.disconnect()

# if __name__ == "__main__":
#     # 测试 send file 与 send track 的速度
#     mtp = MyMTP()
#     mtp.connect()
#     print("Device Name\t\t: %s" % cdec(mtp.get_devicename()))
#     song_name = "Joe Hisaishi-天空之城(木吉他).mp3"  # 6.15MB (6,453,614Bytes)
#     source = os.path.join(SONG_DIR, song_name)
#     target = generate_dst_song_name(song_name)
#
#     from timeit import Timer
#     t_f =
#       Timer("mtp.send_file_from_file(source, 'file_' + target, parent=4)",
#             "from __main__ import mtp, source, target")
#     t_t = Timer("mtp.sendtrack(source, 'track_' + target, parent=4)",
#                                "from __main__ import mtp, source, target")
#     print("send from file use: %ss" % t_f.timeit(1))   # 0.28895487400586717s
#     print("send from track use: %ss" % t_t.timeit(1))  # 0.3443506720068399s
#
#     mtp.disconnect()


def send_pic():
    mtp = pymtp.MTP()
    mtp.connect()
    print("Device Name : %s" % cdec(mtp.get_devicename()))
    pic_name = "Screenshot from 2014-09-01 12:52:55.png"
    pic_dir = os.path.expanduser("~/Pictures")
    source = os.path.join(pic_dir, pic_name)
    target = pic_name
    def_pic_dir = mtp.device.contents.default_picture_folder
    item_id = mtp.send_file_from_file(source, target, parent=def_pic_dir)
    print(
        dedent("Create new file with\
            ID: %s for File: %s" % (item_id, target)))
    mtp.disconnect()


if __name__ == "__main__":
    main3()
