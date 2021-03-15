#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from html.parser import HTMLParser
from urllib.request import urlopen


class MoviesItemsParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.json_link = None

    def error(self, message):
        xbmc.log("NewsItemsParser error")

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for name, value in attrs:
                if name == 'data-playlist-url':
                    self.json_link = 'https://www.1tv.ru' + value

    def get_movies_items(self):
        json_data = urlopen(self.json_link).read()
        return json.loads(json_data)
