# VERSION: 1.0
# AUTHOR: Potato

from helpers import retrieve_url
from novaprinter import prettyPrinter
from html.parser import HTMLParser

class x1337x(object):
    url = 'https://1337x.to'
    name = '1337x'
    supported_categories = {'all': 'search'}

    class Parser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.inside_table = False
            self.inside_row = False
            self.col_idx = 0
            self.current_row = {}
            self.results = []

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'table' and 'table-list' in attrs.get('class', ''):
                self.inside_table = True
            elif self.inside_table and tag == 'tr':
                self.inside_row = True
                self.col_idx = 0
                self.current_row = {}
            elif self.inside_row and tag == 'a' and 'href' in attrs:
                self.current_row['detail_url'] = attrs['href']

        def handle_endtag(self, tag):
            if tag == 'table' and self.inside_table:
                self.inside_table = False
            elif tag == 'tr' and self.inside_row:
                self.inside_row = False
                if self.current_row.get('name'):
                    self.results.append(self.current_row)

        def handle_data(self, data):
            if self.inside_row:
                text = data.strip()
                if text:
                    # Take first non-empty data as name
                    if 'name' not in self.current_row:
                        self.current_row['name'] = text

    def search(self, what, cat='all'):
        url = f"{self.url}/search/{what}/1/"
        html = retrieve_url(url)
        parser = self.Parser()
        parser.feed(html)
        for row in parser.results:
            # Try to fetch the magnet link from the detail page
            magnet = ''
            desc_link = self.url + row.get('detail_url', '')
            try:
                detail_html = retrieve_url(desc_link)
                i = detail_html.find('magnet:?xt=')
                if i != -1:
                    j = detail_html.find('"', i)
                    magnet = detail_html[i:j]
            except Exception:
                pass
            res = {
                'name': row.get('name', ''),
                'link': magnet,
                'size': '',
                'seeds': '',
                'leech': '',
                'engine_url': self.url,
                'desc_link': desc_link
            }
            prettyPrinter(res)
