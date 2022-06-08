#!/usr/bin/env python3

from typing import final
from bs4 import BeautifulSoup
from pprint import pprint

import re
import requests
import logging
import time

logging.basicConfig(level=logging.DEBUG)
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
    # takes the main table from get_pokemon_data
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

def parse_misc_details(dextable):
    misc_info = dextable.find_all('td', {'class': 'foo'})

    # grabs the classification, height, and weight text
    misc_info_names = [i.text for i in misc_info]
    
    # moves up, then grabs the tr with the values of the above
    tr_of_misc_info = misc_info[0].parent.find_next_sibling('tr')
    raw_values = [i.text for i in tr_of_misc_info.find_all('td')]

    #parses the raw values, drops the imperial units if they exist, then appends it to a final list
    misc_info_values = []
    for value in raw_values:
        try:
            misc_info_values.append(value.split('\r\n\t\t\t')[1])
        except IndexError:
            misc_info_values.append(value)

    # converts both above lists to a dict to be appended to the entry
    final_dict = dict(zip(misc_info_names, misc_info_values))
    return final_dict

def get_evolution_line(evotable):
    all_td_pkmn = evotable.find_all('td', {'class': 'pkmn'})
    pprint(all_td_pkmn)
    all_evos = []
    for pokemon in all_td_pkmn:
        try:
            link = pokemon.find('a', {'href': re.compile(r'\/pokemon\/\w+')}).get('href')
            all_evos.append(link.split('/')[-1])
        except AttributeError:
            print("Error?")
            print(pokemon)
        
    
    final_dict = {}
    count = 1
    for mon in all_evos:
        if count == 1:
            final_dict['Base'] = mon
            count += 1
        elif count > 3:
            final_dict['Mega'] = 'Yes'
            count += 1
        else:
            final_dict[f'Stage {count-1}'] = mon
            count += 1

    return final_dict

def get_pokemon_data(url):
    # I create the pokemon entries individually, then append them to the final dict at the end.
    pokemon_entry = {}
    
    base_mon_page = requests.get(url)
    base_mon_soup = BeautifulSoup(base_mon_page.text, "html.parser")

    main_table = base_mon_soup.find('table', {'class': 'dextable'})
    evotable = base_mon_soup.find('table', {'class': 'evochain'})

    pokemon_entry["Name"] = get_pokemon_name(main_table)

    # sort pokemon types, checking for single types over dual types
    pokemon_type = get_pokemon_types(main_table)
    pokemon_entry["Type"] = {}
    pokemon_entry["Type"]["Primary"] = pokemon_type[0] 
    try:
        pokemon_entry["Type"]["Secondary"] = pokemon_type[1]
    except IndexError:
        pokemon_entry["Type"]["Secondary"] = "None"
    
    pokemon_entry["Dex Number"] = get_pokedex_numbers(main_table)
    pokemon_entry.update(parse_misc_details(main_table))

    pokemon_entry["Evolution Chain"] = get_evolution_line(evotable)
    generation_links = get_generation_links(url)
    pprint(pokemon_entry)

if __name__ == '__main__':
    get_pokemon_data('https://serebii.net/pokemon/nidoranf/')

    # national_dex_url = BASE_URL + NATIONAL_DEX_URL

    # all_pokemon = get_national_dex(national_dex_url)
    # for link in all_pokemon:
    #     get_pokemon_data(BASE_URL + link)
        