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
from novaprinter import prettyPrinter

class leetx(object):
    url = 'https://1337x.to'
    name = '1337x'
    supported_categories = {
        'all': 'all',
        'anime': 'anime',
        'books': 'books', 
        'games': 'games',
        'movies': 'movies',
        'music': 'music',
        'software': 'software',
        'tv': 'tv'
    }

    def __init__(self):
        pass

    def download_torrent(self, info):
        print(download_file(info))

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
                    cat_map = {
                        'anime': '/cat/Anime',
                        'books': '/cat/Books', 
                        'games': '/cat/Games',
                        'movies': '/cat/Movies',
                        'music': '/cat/Music',
                        'software': '/cat/Applications',
                        'tv': '/cat/TV'
                    }
                    cat_path = cat_map.get(cat, '')
                    if cat_path:
                        search_url = f'{self.url}{cat_path}/{page}/'
                    else:
                        search_url = f'{self.url}/search/{what}/{page}/'
                
                # Get page content
                data = retrieve_url(search_url)
                if not data:
                    break
                    
                # Parse results using regex (more reliable)
                self.parse_results(data)
                    
            except Exception:
                break

    def parse_results(self, data):
        """Parse search results using regex"""
        try:
            # Find all torrent rows in the table
            torrent_pattern = r'<tr[^>]*>.*?</tr>'
            rows = re.findall(torrent_pattern, data, re.DOTALL)
            
            for row in rows:
                # Skip header rows
                if 'th>' in row or 'Type' in row:
                    continue
                    
                # Extract torrent name and description link
                name_pattern = r'<a[^>]*href="(/torrent/[^"]*)"[^>]*>([^<]+)</a>'
                name_match = re.search(name_pattern, row)
                if not name_match:
                    continue
                    
                desc_link = f"https://1337x.to{name_match.group(1)}"
                name = name_match.group(2).strip()
                
                # Extract magnet link
                magnet_pattern = r'href="(magnet:[^"]*)"'
                magnet_match = re.search(magnet_pattern, row)
                if not magnet_match:
                    continue
                    
                magnet_link = magnet_match.group(1)
                
                # Extract size (look for patterns like "1.2 GB", "500 MB", etc.)
                size_pattern = r'(\d+(?:\.\d+)?\s*[KMGT]?B)'
                size_match = re.search(size_pattern, row, re.IGNORECASE)
                size = size_match.group(1) if size_match else '-1'
                
                # Extract seeds and leeches (look for numbers in table cells)
                numbers = re.findall(r'>(\d+(?:,\d+)?)<', row)
                seeds = numbers[0].replace(',', '') if len(numbers) > 0 else '-1'
                leech = numbers[1].replace(',', '') if len(numbers) > 1 else '-1'
                
                # Create result dict
                result = {
                    'link': magnet_link,
                    'name': name,
                    'size': size,
                    'seeds': seeds,
                    'leech': leech,
                    'engine_url': 'https://1337x.to',
                    'desc_link': desc_link,
                    'pub_date': '-1'
                }
                
                # Print result
                prettyPrinter(result)
                
        except Exception:
            pass
