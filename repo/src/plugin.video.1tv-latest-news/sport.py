#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
from html.parser import HTMLParser
from urllib.request import urlopen


class SportDirectoryParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.process_links = False
        self.process_data = False
        self.links_cache = []

    def error(self, message):
        xbmc.log("SportDirectoryParser error")

    def handle_starttag(self, tag, attrs):
        if tag == 'header':
            for name, value in attrs:
                if name == 'id' and value == 'page-title':
                    self.process_links = True

        if tag == 'a' and self.process_links:
            for name, value in attrs:
                if name == 'href' and '/sport/' in value:
                    self.links_cache.append({'href': value})

    def handle_data(self, data):
        if self.process_links and self.lasttag == 'span':
            if len(self.links_cache) == 0:
                return
            data = re.sub(r'[\W]+', ' ', data, flags=re.UNICODE)  # strip all non alphanumeric characters
            self.links_cache[-1]['name'] = data

    def handle_endtag(self, tag):
        if self.process_links:
            if tag == 'header':
                self.process_links = False

    def get_sport_directory(self):
        return self.links_cache


class SportItemsParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.json_link = None

    def error(self, message):
        xbmc.log("SportItemsParser error")

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for name, value in attrs:
                if 'data-playlist-url' in name:
                    self.json_link = 'https://www.1tv.ru' + value

    def get_sport_items(self):
        json_data = urlopen(self.json_link).read()
        return json.loads(json_data)
