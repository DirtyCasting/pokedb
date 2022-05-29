#!/usr/bin/env python3

from bs4 import BeautifulSoup
from pprint import pprint

import re
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
BASE_URL = "https://www.serebii.net"
NATIONAL_DEX_URL = "/pokemon/nationalpokedex.shtml"


def get_national_dex(dex_url):
    dex_page = requests.get(dex_url)
    soup = BeautifulSoup(dex_page.text, "html.parser")

    # dextable is the main table that holds all the pokemon links
    dextable = soup.find("table", {'class': 'dextable'}) 
    pokemon_urls = []
    
    # find all '/pokemon/{anything} links'
    # if you were to ask me to explain this regex, I could do it.  '/pokemon/<any number of word chars past that>'
    for link in dextable.findAll('a', {'href': re.compile(r'\/pokemon\/\w+')}):
        # remove all '/pokemon/type/{type} links' 
        if not re.match(r'\/pokemon\/type\/\w+', link.get("href")):
            pokemon_urls.append(link.get("href"))
    
    # go over the list and remove duplicates
    pokemon_urls = [i for n, i in enumerate(pokemon_urls) if i not in pokemon_urls[:n]]
    return pokemon_urls

def get_generation_links(url):
    # pokedex link regex: \/pokedex\-?\w*\/\S+
    # I could not explain that to you.  It just works.  For now.
    # Aubrey will probably end up regretting that later down the line. -Aubrey.

    base_mon_page = requests.get(url)
    soup = BeautifulSoup(base_mon_page.text, "html.parser")

    # block_year is the name of each div that links to a mon's generation page
    block_years = [link for link in soup.findAll('div', {"class": "block_year"})]
    dex_links = []
    # finds the link to each generations pokedex, then appends them to dex_links.
    for block_year in block_years:
        dex_link = block_year.find('a', {'href': re.compile(r'\/pokedex\-?\w*\/\S+')})

        # Hacky way to not add None's to the list.  The line short circuits if dex_link = None/NoneType
        dex_link and dex_links.append(dex_link.get('href'))

    return dex_links

def get_pokemon_data(url):
    print("placeholder poke_data")
    

if __name__ == '__main__':
    national_dex_url = BASE_URL + NATIONAL_DEX_URL
    final_dict = {}

    all_pokemon = get_national_dex(national_dex_url)
    for link in all_pokemon:
        generation_dex_links = get_generation_links(BASE_URL + link)
        for link in generation_dex_links:
            get_pokemon_data(BASE_URL + link)