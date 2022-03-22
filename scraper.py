#!/usr/bin/env python3
import requests
import re
from bs4 import BeautifulSoup
from pprint import pprint
import os
import time

base_url = "https://bulbapedia.bulbagarden.net"
master_list = []

def get_master_list():
    national_dex_url = "/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number"
    national_dex_page = requests.get(base_url + national_dex_url)
    data = national_dex_page.text

    html = BeautifulSoup(data, 'html.parser')
    tables = html.findAll("table")
    pokemon_links = []

    # nested for loop intended to find all the links in each table, then append them to the
    # master list above (pokemon_links) after checking for duplicates
    for table in tables:
        for link in table.findAll("a", attrs={"href": re.compile("/wiki/.+\(Pok%C3%A9mon\)")}):
            potential = link.get("href")
            if potential not in pokemon_links:
                pokemon_links.append(potential)
    
    return pokemon_links



master_list += (get_master_list())
os.mkdir('./wiki')

for pokemon_page in master_list:
    print(f"Fetching '{pokemon_page}'...")
    page = requests.get(base_url + pokemon_page)
    soup = BeautifulSoup(page.text, 'html.parser')
    pokemon_name = soup.title.text.split()[0]

    with open(f'wiki/{pokemon_name}.html', 'w+') as pokemon_file:
        pokemon_file.write(page.text)
    time.sleep(1)    

