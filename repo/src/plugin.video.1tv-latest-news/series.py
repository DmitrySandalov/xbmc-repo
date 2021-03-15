#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from html.parser import HTMLParser
from urllib.request import urlopen


class SeriesDirectoryParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.process_links = False
        self.links_cache = []

    def error(self, message):
        xbmc.log("SeriesDirectoryParser error")

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for name, value in attrs:
                if name == 'class' and 'secondary_submenu_wrapper' in value:
                    self.process_links = True

        if tag == 'a' and self.process_links:
            for name, value in attrs:
                if name == 'href' and '/movies/' in value:
                    self.links_cache.append({'href': value})

        if tag == 'button':
            for name, value in attrs:
                if name == 'class' and value == 'sub-menu-toggle':
                    self.process_links = False

    def handle_data(self, data):
        if self.process_links and self.lasttag == 'a':
            self.links_cache[-1]['name'] = data

    def handle_endtag(self, tag):
        pass

    def get_series_directory(self):
        return self.links_cache


class SeriesItemsParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.json_link = None

    def error(self, message):
        xbmc.log("SeriesItemsParser error")

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for name, value in attrs:
                if 'data-playlist-url' in name:
                    self.json_link = 'https://www.1tv.ru' + value

    def get_series_items(self):
        json_data = urlopen(self.json_link).read()
        return json.loads(json_data)
