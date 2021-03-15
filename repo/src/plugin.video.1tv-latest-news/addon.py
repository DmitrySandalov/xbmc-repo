#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Kodi plugin: play media from 1tv (Russia).

"""

from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.request import urlopen

import sys
import xbmc
import xbmcgui
import xbmcplugin

from doc import DocDirectoryParser, DocItemsParser
from movies import MoviesItemsParser
from news import NewsItemsParser
from series import SeriesDirectoryParser, SeriesItemsParser
from shows import ShowDirectoryParser, ShowItemsParser
from sport import SportDirectoryParser, SportItemsParser

__author__ = "Dmitry Sandalov"
__copyright__ = "Copyright 2014-2021, Dmitry Sandalov"
__credits__ = []
__license__ = "GNU GPL v2.0"
__version__ = "2.1.0"
__maintainer__ = "Dmitry Sandalov"
__email__ = "dmitry@sandalov.org"
__status__ = "Development"

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')


def add_directory_items(dir_items, is_folder):
    for item in dir_items:
        li_item = xbmcgui.ListItem(item['title'])
        if is_folder:
            url_item = build_url({'mode': 'folder', 'foldername': item['name']})
        elif item['material_type'] == 'video_material':
            url_item = get_url_for_item(item)
        elif item['material_type'] == 'stream_material':
            # Ensure that 'InputStream Adaptive' is installed and enabled
            # Add-ons -> VideoPlayer InputStream -> InputStream Adaptive
            url_item = get_url_for_stream_item(item)
            li_item.setMimeType('application/xml+dash')
            li_item.setProperty('MimeType', 'application/xml+dash')
            li_item.setProperty('inputstream', 'inputstream.adaptive')
            li_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        else:
            xbmc.log("Not a folder and unable to get url_item")
            continue
        if 'poster' in item:
            li_item.setArt({'icon': item['poster']})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url_item,
                                    listitem=li_item, isFolder=is_folder)
    xbmcplugin.endOfDirectory(addon_handle)


def get_sport_directory():
    all_sport = 'https://www.1tv.ru/sport?all'
    html = urlopen_safe(all_sport)
    parser = SportDirectoryParser()
    parser.feed(html)
    return parser.get_sport_directory()


def get_shows_directory():
    all_shows = 'https://www.1tv.ru/shows?all'
    html = urlopen_safe(all_shows)
    parser = ShowDirectoryParser()
    parser.feed(html)
    return parser.get_shows_directory()


def get_doc_directory():
    all_doc = 'https://www.1tv.ru/doc'
    html = urlopen_safe(all_doc)
    parser = DocDirectoryParser()
    parser.feed(html)
    return parser.get_doc_directory()


def get_series_directory():
    all_series = 'https://www.1tv.ru/movies/vse-filmy'
    html = urlopen_safe(all_series)
    parser = SeriesDirectoryParser()
    parser.feed(html)
    return parser.get_series_directory()


def add_sport_items(folder):
    sport_link = 'https://www.1tv.ru' + folder
    html = urlopen_safe(sport_link)
    parser = SportItemsParser()
    parser.feed(html)
    sport_items = parser.get_sport_items()
    add_directory_items(sport_items, is_folder=False)


def add_show_items(folder):
    show_link = 'https://www.1tv.ru' + folder
    html = urlopen_safe(show_link)
    parser = ShowItemsParser()
    parser.feed(html)
    show_items = parser.get_show_items()
    add_directory_items(show_items, is_folder=False)


def add_doc_items(folder):
    doc_link = 'https://www.1tv.ru' + folder
    html = urlopen_safe(doc_link)
    parser = DocItemsParser()
    parser.feed(html)
    doc_items = parser.get_doc_items()
    add_directory_items(doc_items, is_folder=False)


def add_series_items(folder):
    series_link = 'https://www.1tv.ru' + folder
    html = urlopen_safe(series_link)
    parser = SeriesItemsParser()
    parser.feed(html)
    series_items = parser.get_series_items()
    add_directory_items(series_items, is_folder=False)


def add_news_items():
    news_link = 'https://www.1tv.ru/news/issue'
    html = urlopen_safe(news_link)
    parser = NewsItemsParser()
    parser.feed(html)
    news_items = parser.get_news_items()
    add_directory_items(news_items, is_folder=False)


def add_movies_items():
    movies_link = 'https://www.1tv.ru/movies/vse-filmy'
    html = urlopen_safe(movies_link)
    parser = MoviesItemsParser()
    parser.feed(html)
    movies_items = parser.get_movies_items()
    add_directory_items(movies_items, is_folder=False)


def get_url_for_item(item):
    res = check_resolution(item)
    url_item = ''
    try:
        url_parts = item['mbr'][res]['src'].rsplit('_', 1)
        url_parts1 = url_parts[1].split('.')
        bitrate = url_parts1[0]
        extension = url_parts1[1]
        url_item = "https:" + url_parts[0] + "_," + bitrate + ",." \
                   + extension + ".urlset/master.m3u8"
    except IndexError:
        xbmc.log("Cannot find link for current resolution")
    if not url_item:
        url_item = 'https:' + item['mbr'][res]['src']
    return url_item


def get_url_for_stream_item(item):
    link = "https://edge2.1internet.tv/dash-live11/streams/1tv/1tvdash.mpd"
    if item and "stream_begin_at" in item:
        link += "?e=%s" % item["stream_begin_at"]
    return link


def build_url(query):
    """Plugin navigation."""
    return base_url + '?' + urlencode(query)


def urlopen_safe(link):
    """Handle network issues."""
    while True:
        try:
            return urlopen(link).read().decode('utf-8')
        except IOError:
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
        {'name': 'news', 'title': 'Новости'},
        {'name': 'shows', 'title': 'Шоу'},
        {'name': 'movies', 'title': 'Фильмы'},
        {'name': 'doc', 'title': 'Доккино'},
        {'name': 'series', 'title': 'Сериалы'},
        {'name': 'sport', 'title': 'Спорт'}
    ]
    add_directory_items(root_items, is_folder=True)

elif mode[0] == 'folder':
    foldername = args['foldername'][0]

    if foldername == 'shows':
        shows = []
        show_links = get_shows_directory()
        for show in show_links:
            if 'stream' not in show['href']:
                shows.append({'title': show['name'], 'name': show['href']})
        add_directory_items(shows, is_folder=True)
    elif '/shows/' in foldername:
        add_show_items(foldername)
    elif foldername == 'sport':
        sports = []
        sport_links = get_sport_directory()
        for sport in sport_links:
            if 'stream' not in sport['href']:
                sports.append({'title': sport['name'], 'name': sport['href']})
        add_directory_items(sports, is_folder=True)
    elif '/sport/' in foldername:
        add_sport_items(foldername)
    elif foldername == 'doc':
        docs = []
        doc_links = get_doc_directory()
        for doc in doc_links:
            docs.append({'title': doc['name'], 'name': doc['href']})
        add_directory_items(docs, is_folder=True)
    elif '/doc/' in foldername:
        add_doc_items(foldername)
    elif foldername == 'news':
        add_news_items()
    elif foldername == 'movies':
        add_movies_items()
    elif foldername == 'series':
        series = []
        series_links = get_series_directory()
        for series_item in series_links:
            if 'stream' not in series_item['href']:
                series.append({'title': series_item['name'], 'name': series_item['href']})
        add_directory_items(series, is_folder=True)
    elif '/movies/' in foldername:
        add_series_items(foldername)
    else:
        url = 'http://localhost/not_supported_yet.mkv'
        li = xbmcgui.ListItem(
            foldername + ' (not supported)')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
        xbmcplugin.endOfDirectory(addon_handle)
