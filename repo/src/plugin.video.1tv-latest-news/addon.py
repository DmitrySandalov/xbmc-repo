#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Kodi plugin: plays latest news from Russian 1tv.

"""

import sys
import urllib2
from xml.etree import ElementTree
from HTMLParser import HTMLParser
import xbmc
import xbmcgui
import xbmcplugin

__author__ = "Dmitry Sandalov"
__copyright__ = "Copyright 2014, Dmitry Sandalov"
__credits__ = []
__license__ = "GNU GPL v2.0"
__version__ = "1.0.2"
__maintainer__ = "Dmitry Sandalov"
__email__ = "dmitry@sandalov.org"
__status__ = "Development"

class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href" and 'swfxml' in value:
                    self.links.append(value)

    def get_latest(self):
        return self.links[0].replace('newsvideolist', 'newsvyp')

addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'movies')

news_archive = 'http://www.1tv.ru/newsvideoarchive/'
html = urllib2.urlopen(news_archive).read()
parser = MyHTMLParser()
parser.feed(html)
last_edition = parser.get_latest()

xml = urllib2.urlopen(last_edition)
tree = ElementTree.parse(xml)
root = tree.getroot()
namespace = "{http://search.yahoo.com/mrss/}"

items = []
total = 0
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
xbmc.PlayList.clear(playlist)
for item in root.getiterator('item'):
    url = item.find(namespace + "content").attrib['url']
    title = item.find('title').text
    img = item.find(namespace + "thumbnail").attrib['url']
    li = xbmcgui.ListItem(label=title, iconImage=img, thumbnailImage=img)
    items.append((url, li, False,))
    total += 1
    playlist.add(url=url, listitem=li, index=total)

xbmcplugin.addDirectoryItems(addon_handle, items, totalItems=total)
xbmc.Player().play(playlist)

xbmcplugin.endOfDirectory(addon_handle)
