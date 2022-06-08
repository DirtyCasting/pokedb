#!/usr/bin/env python3

from typing import final
from bs4 import BeautifulSoup
from pprint import pprint

import re
import requests
import logging

BASE_URL = "https://www.serebii.net"
NATIONAL_DEX_URL = "/pokemon/nationalpokedex.shtml"
FINAL_DICT = {}


def convert_list_to_dict(input_dict):
    it = iter(input_dict)
    result_dict = dict(zip(it, it))
    return result_dict

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

def get_pokemon_name(dextable):
    english = dextable.find('b', text=re.compile('English'))
    pokemon = english.parent.find_next_sibling('td').text

    return pokemon

def get_pokemon_types(dextable):
    # takes the first table from get_pokemon_data
    type_cell = dextable.find('td', {'class': 'cen'})
    type_hrefs = type_cell.find_all('a', {'href': re.compile(r'\/pokemon\/type\/(\w+)')})

    #puts the final two types into a list, then returns them to be sorted later
    final_type = []
    for pokemon_type in type_hrefs:
        type_a = pokemon_type.get('href')
        final_type.append(type_a.removeprefix("/pokemon/type/"))
    return final_type

def get_pokedex_numbers(dextable):
    # grab cell with dex numbers
    dex_cell = dextable.find_all('td', {'class': 'fooinfo'})[2]
    dex_numbers = dex_cell.find_all('td')

    # Dirty, but works.  Gets the text of the dex numbers, splits off of the colon, and replaces the pound symbol if found
    list_of_dex_numbers = [i.text.split()[0].replace('#', '') for i in dex_numbers]

    return convert_list_to_dict(list_of_dex_numbers)


def get_pokemon_data(url):
    # I create the pokemon entries individually, then append them to the final dict at the end.
    pokemon_entry = {}
    
    base_mon_page = requests.get(url)
    soup = BeautifulSoup(base_mon_page.text, "html.parser")

    first_table = soup.find('table', {'class': 'dextable'})

    pokemon_entry["Name"] = get_pokemon_name(first_table)

    # sort pokemon types, checking for single types over dual types
    pokemon_type = get_pokemon_types(first_table)
    pokemon_entry["Type"] = {}
    pokemon_entry["Type"]["Primary"] = pokemon_type[0] 
    try:
        pokemon_entry["Type"]["Secondary"] = pokemon_type[1]
    except IndexError:
        pokemon_entry["Type"]["Secondary"] = "None"
    
    
    pokemon_entry["Dex Number"] = get_pokedex_numbers(first_table)

    generation_links = get_generation_links(url)
    pprint(pokemon_entry)

if __name__ == '__main__':
    national_dex_url = BASE_URL + NATIONAL_DEX_URL

    all_pokemon = get_national_dex(national_dex_url)
    for link in all_pokemon:
        get_pokemon_data(BASE_URL + link)