#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Kodi plugin: plays latest news from Russian 1tv.

"""

import sys
import datetime
import urllib2
import xml.etree.ElementTree as e
import xbmc
import xbmcgui
import xbmcplugin

__author__ = "Dmitry Sandalov"
__copyright__ = "Copyright 2014, Dmitry Sandalov"
__credits__ = []
__license__ = "GNU GPL v2.0"
__version__ = "1.0.1"
__maintainer__ = "Dmitry Sandalov"
__email__ = "dmitry@sandalov.org"
__status__ = "Development"

addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'movies')

today = datetime.datetime.now()
hour = today.hour

if hour < 10:
    today -= datetime.timedelta(days=1)
    stamp_hour = '11'
elif 10 <= hour < 13:
    stamp_hour = '5'
elif 13 <= hour < 16:
    stamp_hour = '7'
elif 16 <= hour < 19:
    stamp_hour = '9'
elif 19 <= hour < 22:
    stamp_hour = '10'
elif 22 <= hour <= 23:
    stamp_hour = '11'

today = today.strftime('%d.%m.%Y')
url = 'http://www.1tv.ru/swfxml/newsvyp/' + today + '/' + stamp_hour

xml = urllib2.urlopen(url)
tree = e.parse(xml)
root = tree.getroot()
namespace = "{http://search.yahoo.com/mrss/}"

items = []
total = 0
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
xbmc.PlayList.clear(playlist)
for item in root.iter('item'):
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
