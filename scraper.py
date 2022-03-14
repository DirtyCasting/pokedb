#!/usr/bin/env python3
import requests
import re
from bs4 import BeautifulSoup
from pprint import pprint

national_dex_url = "https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number"
national_dex_page = requests.get(national_dex_url)
data = national_dex_page.text

html = BeautifulSoup(data, 'html.parser')
tables = html.findAll("table")
pokemon_links = []

# nested for loop intended to find all the links in each table, then append them to the master list above (pokemon_links)
for table in tables:
    for link in table.findAll("a", attrs={"href": re.compile("/wiki/.+\(Pok%C3%A9mon\)")}):
        potential = link.get("href")
        if potential not in pokemon_links:
            pokemon_links.append(potential)

pprint(pokemon_links)