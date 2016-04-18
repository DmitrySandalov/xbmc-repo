#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Kodi plugin: plays latest news from Russian 1tv.

"""

import sys
import urllib2
import json
from HTMLParser import HTMLParser
import xbmc
import xbmcgui
import xbmcplugin

__author__ = "Dmitry Sandalov"
__copyright__ = "Copyright 2016, Dmitry Sandalov"
__credits__ = []
__license__ = "GNU GPL v2.0"
__version__ = "1.0.5"
__maintainer__ = "Dmitry Sandalov"
__email__ = "dmitry@sandalov.org"
__status__ = "Development"

class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "div" and 'data-playlist-url' in attrs_dict:
            self.links.append(attrs_dict['data-playlist-url'])

    def get_latest(self):
        return self.links[0].replace('/video_materials.json', 'http://www.1tv.ru/video_materials.json')


def message():
    dialog = xbmcgui.Dialog()
    return dialog.yesno(heading="No connection",
                        line1="Check your connection and try again",
                        nolabel="Exit", yeslabel="Retry")


def get_last_edition():
    news_archive = 'http://www.1tv.ru/news/issue'
    html = urllib2.urlopen(news_archive).read()
    parser = MyHTMLParser()
    parser.feed(html)
    last_edition_link = parser.get_latest()
    return urllib2.urlopen(last_edition_link)

addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'movies')

edition = ''
while True:
    try:
        edition = get_last_edition()
    except urllib2.URLError:
        retry = message()
        if retry:
            continue
        else:
            sys.exit()
    break

edition_items = json.load(edition)

items = []
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
xbmc.PlayList.clear(playlist)
for item in edition_items:
    url = "http:" + item['mbr'][0]['src']
    title = item['title']
    img = "http:" + item['poster']
    li = xbmcgui.ListItem(label=title, iconImage=img, thumbnailImage=img)
    items.append((url, li, False,))
    playlist.add(url=url, listitem=li, index=len(items))

xbmcplugin.addDirectoryItems(addon_handle, items, totalItems=len(items))
xbmc.Player().play(playlist)

xbmcplugin.endOfDirectory(addon_handle)
