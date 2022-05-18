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
    dextable = soup.find("table", {'class': 'dextable'}) # dextable is the main table that holds all the pokemon links
    pokemon_urls = []
    for link in dextable.findAll('a', {'href': re.compile(r'\/pokemon\/\w+')}): # find all '/pokemon/{anything} links'
        if not re.match(r'\/pokemon\/type\/\w+', link.get("href")): # remove all '/pokemon/type/{type} links'
            pokemon_urls.append(link.get("href"))
    pokemon_urls = [i for n, i in enumerate(pokemon_urls) if i not in pokemon_urls[:n]] # go over the list and remove duplicates
    return pokemon_urls

def get_pokemon_data(url):
    pokemon_page = requests.get(url)
    soup = BeautifulSoup(pokemon_page.text, 'html.parser')
    

if __name__ == '__main__':
    national_dex_url = BASE_URL + NATIONAL_DEX_URL
    all_pokemon = get_national_dex(national_dex_url)
    for link in all_pokemon:
        get_pokemon_data(BASE_URL + link)
