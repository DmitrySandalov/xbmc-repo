#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Kodi plugin: play media from 1tv (Russia).

"""

import sys
import urllib
import urlparse
import exceptions

import xbmcgui
import xbmcplugin

from shows import ShowDirectoryParser, ShowItemsParser
from doc import DocDirectoryParser, DocItemsParser
from news import NewsItemsParser

__author__ = "Dmitry Sandalov"
__copyright__ = "Copyright 2017, Dmitry Sandalov"
__credits__ = []
__license__ = "GNU GPL v2.0"
__version__ = "1.0.9"
__maintainer__ = "Dmitry Sandalov"
__email__ = "dmitry@sandalov.org"
__status__ = "Development"

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')


def add_directory_items(dir_items):
    for item in dir_items:
        url_item = build_url({'mode': 'folder', 'foldername': item['name']})
        li_item = xbmcgui.ListItem(item['title'], iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url_item,
                                    listitem=li_item, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)


def get_shows_directory():
    all_shows = 'https://www.1tv.ru/shows?all'
    html = urlopen_safe(all_shows)
    parser = ShowDirectoryParser()
    parser.feed(html)
    return parser.get_shows_directory()


def add_show_items(folder):
    show_link = 'https://www.1tv.ru' + folder
    html = urlopen_safe(show_link).decode("utf8")
    parser = ShowItemsParser()
    parser.feed(html)
    show_items = parser.get_show_items()

    for show_item in show_items:
        res = check_resolution(show_item)
        url_item = 'http:' + show_item['mbr'][res]['src']
        li_item = xbmcgui.ListItem(
            show_item['title'], iconImage='http:' + show_item['poster'])
        xbmcplugin.addDirectoryItem(
            handle=addon_handle, url=url_item, listitem=li_item)
    xbmcplugin.endOfDirectory(addon_handle)
    return []


def get_doc_directory():
    all_doc = 'https://www.1tv.ru/doc'
    html = urlopen_safe(all_doc)
    parser = DocDirectoryParser()
    parser.feed(html)
    return parser.get_doc_directory()


def add_doc_items(folder):
    doc_link = 'https://www.1tv.ru' + folder
    html = urlopen_safe(doc_link).decode("utf8")
    parser = DocItemsParser()
    parser.feed(html)
    doc_items = parser.get_doc_items()

    for doc_item in doc_items:
        res = check_resolution(doc_item)
        url_item = 'http:' + doc_item['mbr'][res]['src']
        li_item = xbmcgui.ListItem(
            doc_item['title'], iconImage='http:' + doc_item['poster'])
        xbmcplugin.addDirectoryItem(
            handle=addon_handle, url=url_item, listitem=li_item)
    xbmcplugin.endOfDirectory(addon_handle)
    return []


def add_news_items():
    news_link = 'https://www.1tv.ru/news/issue'
    html = urlopen_safe(news_link).decode("utf8")
    parser = NewsItemsParser()
    parser.feed(html)
    news_items = parser.get_news_items()

    for news in news_items:
        res = check_resolution(news)
        url_item = 'http:' + news['mbr'][res]['src']
        li_item = xbmcgui.ListItem(
            news['title'], iconImage='http:' + news['poster'])
        xbmcplugin.addDirectoryItem(
            handle=addon_handle, url=url_item, listitem=li_item)
    xbmcplugin.endOfDirectory(addon_handle)
    return []


def build_url(query):
    """Plugin navigation."""
    return base_url + '?' + urllib.urlencode(query)


def urlopen_safe(link):
    """Handle network issues."""
    while True:
        try:
            return urllib.urlopen(link).read()
        except exceptions.IOError:
            retry = err_no_connection()
            if retry:
                continue
            else:
                sys.exit()


def err_no_connection():
    """Display a network error message."""
    dialog = xbmcgui.Dialog()
    return dialog.yesno(heading="No connection",
                        line1="Check your connection and try again",
                        nolabel="Exit", yeslabel="Retry")


def check_resolution(video):
    """
    Select the best resolution with respect to settings.
    (Some video files have only one resolution.)
    :param video: list of formats for selected video
    :return: resolution
    """
    max_res = len(video['mbr'])
    return resolution \
        if max_res >= resolution + 1 \
        else max_res - 1


# Gets resolution from plugin settings
resolutions_dict = {'hd': 0, 'sd': 1, 'ld': 2}
resolution_setting = xbmcplugin.getSetting(addon_handle, 'video_res')
resolution = resolutions_dict[resolution_setting.lower()]

mode = args.get('mode', None)

if mode is None:
    root_items = [
        # {'name': 'live', 'title': 'Прямой эфир (TODO)'},
        {'name': 'shows', 'title': 'Телепроекты'},
        {'name': 'news', 'title': 'Новости'},
        # {'name': 'movies', 'title': 'Фильмы и сериалы (TODO)'},
        {'name': 'doc', 'title': 'Доккино'}
    ]
    add_directory_items(root_items)

elif mode[0] == 'folder':
    foldername = args['foldername'][0]

    if foldername == 'shows':
        shows = []
        show_links = get_shows_directory()
        for show in show_links:
            if 'stream' not in show['href']:
                shows.append({'title': show['name'], 'name': show['href']})
        add_directory_items(shows)
    elif '/shows/' in foldername:
        add_show_items(foldername)
    elif foldername == 'doc':
        docs = []
        doc_links = get_doc_directory()
        for doc in doc_links:
            docs.append({'title': doc['name'], 'name': doc['href']})
        add_directory_items(docs)
    elif '/doc/' in foldername:
        add_doc_items(foldername)
    elif foldername == 'news':
        add_news_items()
    else:
        url = 'http://localhost/not_supported_yet.mkv'
        li = xbmcgui.ListItem(
            foldername + ' (not supported)', iconImage='DefaultVideo.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
        xbmcplugin.endOfDirectory(addon_handle)
