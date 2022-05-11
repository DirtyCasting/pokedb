#!/usr/bin/env python3

from bs4 import BeautifulSoup
from pprint import pprint

import requests

# TODO: make this a script arg instead of hardcoding it
FIRST_MON = 1
LAST_MON = 1

def get_pokemon_data(urls):
    for url in urls:
        pokedex_page = requests.get(url)
        soup = BeautifulSoup(pokedex_page.text, "html.parser")
        main_div = soup.find('div', {'id': 'content'})
        pprint(main_div)


if __name__ == '__main__':
    #urls table code inspired by https://github.com/shadforth/pokemon-web-scraper <3
    urls = ['https://serebii.net/pokedex/{}.shtml'.format(str(x).zfill(3))
            for x in range(FIRST_MON, LAST_MON + 1)]
    pprint(urls)
    get_pokemon_data(urls)
    
