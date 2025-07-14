# VERSION: 1.0
# AUTHORS: Your Name (your.email@example.com)

# LICENSING INFORMATION
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

import re
from html.parser import HTMLParser
from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter, anySizeToBytes

class leetx(object):
    url = 'https://1337x.to'
    name = '1337x'
    supported_categories = {
        'all': 'all',
        'anime': 'Anime',
        'books': 'Books', 
        'games': 'Games',
        'movies': 'Movies',
        'music': 'Music',
        'software': 'Applications',
        'tv': 'TV'
    }

    class MyHtmlParser(HTMLParser):
        def error(self, message):
            pass

        def __init__(self):
            HTMLParser.__init__(self)
            self.current_item = None
            self.inside_torrent_row = False
            self.inside_name_cell = False
            self.inside_name_link = False
            self.inside_size_cell = False
            self.inside_seeds_cell = False
            self.inside_leech_cell = False
            self.cell_index = 0
            self.results = []

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            
            # Look for torrent table rows
            if tag == 'tr' and self.inside_torrent_row == False:
                self.inside_torrent_row = True
                self.current_item = {}
                self.cell_index = 0
                return
            
            # Handle table cells
            if self.inside_torrent_row and tag == 'td':
                self.cell_index += 1
                if self.cell_index == 1:  # Name column
                    self.inside_name_cell = True
                elif self.cell_index == 5:  # Size column
                    self.inside_size_cell = True
                elif self.cell_index == 6:  # Seeds column
                    self.inside_seeds_cell = True
                elif self.cell_index == 7:  # Leech column
                    self.inside_leech_cell = True
                return
            
            # Handle name link
            if self.inside_name_cell and tag == 'a':
                href = params.get('href', '')
                if href.startswith('/torrent/'):
                    self.current_item['desc_link'] = f'https://1337x.to{href}'
                    self.inside_name_link = True
                return

        def handle_data(self, data):
            if self.inside_name_link:
                self.current_item['name'] = data.strip()
            elif self.inside_size_cell:
                size_text = data.strip()
                if size_text and size_text != '-':
                    try:
                        self.current_item['size'] = str(anySizeToBytes(size_text))
                    except:
                        self.current_item['size'] = '-1'
            elif self.inside_seeds_cell:
                seeds_text = data.strip()
                if seeds_text and seeds_text.isdigit():
                    self.current_item['seeds'] = seeds_text
            elif self.inside_leech_cell:
                leech_text = data.strip()
                if leech_text and leech_text.isdigit():
                    self.current_item['leech'] = leech_text

        def handle_endtag(self, tag):
            if tag == 'a' and self.inside_name_link:
                self.inside_name_link = False
            elif tag == 'td':
                if self.inside_name_cell:
                    self.inside_name_cell = False
                elif self.inside_size_cell:
                    self.inside_size_cell = False
                elif self.inside_seeds_cell:
                    self.inside_seeds_cell = False
                elif self.inside_leech_cell:
                    self.inside_leech_cell = False
            elif tag == 'tr' and self.inside_torrent_row:
                self.inside_torrent_row = False
                if self.current_item and 'name' in self.current_item and 'desc_link' in self.current_item:
                    self.results.append(self.current_item)
                self.current_item = None

    def __init__(self):
        pass

    def download_torrent(self, info):
        print(download_file(info))

    def get_magnet_link(self, desc_url):
        """Extract magnet link from torrent description page"""
        try:
            data = retrieve_url(desc_url)
            if data:
                # Look for magnet link in the description page
                magnet_match = re.search(r'href="(magnet:[^"]*)"', data)
                if magnet_match:
                    return magnet_match.group(1)
        except:
            pass
        return None

    def search(self, what, cat='all'):
        what = what.replace('%20', '+')
        
        # Search multiple pages
        for page in range(1, 4):  # Search first 3 pages
            try:
                # Build search URL
                if cat == 'all':
                    search_url = f'{self.url}/search/{what}/{page}/'
                else:
                    # Category-specific search
                    category = self.supported_categories.get(cat, '')
                    if category and category != 'all':
                        search_url = f'{self.url}/category-search/{what}/{category}/{page}/'
                    else:
                        search_url = f'{self.url}/search/{what}/{page}/'
                
                # Get page content
                data = retrieve_url(search_url)
                if not data:
                    break
                
                # Parse results using HTMLParser
                parser = self.MyHtmlParser()
                parser.feed(data)
                parser.close()
                
                # Process results
                for item in parser.results:
                    # Get magnet link from description page
                    magnet_link = self.get_magnet_link(item['desc_link'])
                    if magnet_link:
                        result = {
                            'link': magnet_link,
                            'name': item['name'],
                            'size': item.get('size', '-1'),
                            'seeds': item.get('seeds', '-1'),
                            'leech': item.get('leech', '-1'),
                            'engine_url': self.url,
                            'desc_link': item['desc_link'],
                            'pub_date': '-1'
                        }
                        prettyPrinter(result)
                    
            except Exception as e:
                break
