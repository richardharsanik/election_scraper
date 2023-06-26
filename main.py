# """
# projekt_3.py: treti projekt do Engeto Online Python Akademie
# author: Richard Harsanik
# email: richard.harsanik@gmail.com
# discord: nakazeny#6042
# """

import requests
from bs4 import BeautifulSoup
import argparse
import csv
from urllib.parse import urljoin

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-link', type=str, required=True, help="link na vyscrapovanie")
    parser.add_argument('-csv', type=str, required=True, help="'nazov.csv' pre vytvorenie suboru s datami")
    arguments = parser.parse_args()
    return arguments.link, arguments.csv

def url_catch(link):
    try:
        response = requests.get(link)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def get_codes_url(link):
    code_elements = url_catch(link).find_all("td", {"class": "cislo"})
    href_list = [urljoin("https://volby.cz/pls/ps2017nss/", x.find("a").get("href")) for x in code_elements]
    return href_list

def get_town_names(link):
    town_elements = url_catch(link).find_all("td",{"class": "overflow_name"})
    town_names = [town.get_text() for town in town_elements]
    return town_names

def sub_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup

def get_registered(codes_url):
    register_list = []
    for url in codes_url:
        sub_soup = sub_url(url)
        registered_elements = sub_soup.find_all("td", {"class": "cislo"}, headers="sa2")
        registered_list = [registered.get_text().replace("\xa0", "") for registered in registered_elements]
        register_list.extend(list(map(int, registered_list)))
    return register_list

def get_envelopes(codes_url):
    envelop_list = []
    for url in codes_url:
        sub_soup = sub_url(url)
        envelopes_elements = sub_soup.find_all("td", {"class": "cislo"}, headers="sa3")
        envelopes_list = [envelopes.get_text().replace("\xa0", "") for envelopes in envelopes_elements]
        envelop_list.extend(list(map(int, envelopes_list)))
    return envelop_list

def get_valid_votes(link):
    validate_list = []
    for url in get_codes_url(link):
        sub_soup = sub_url(url)
        valid_elements = sub_soup.find_all("td", {"class": "cislo"}, headers="sa6")
        valid_list = [valid.get_text().replace("\xa0", "") for valid in valid_elements]
        validate_list.extend(list(map(int, valid_list)))
    return validate_list

def sub_url_partis(link):
    response = requests.get(get_codes_url(link)[0])
    soup = BeautifulSoup(response.text, "html.parser")
    return soup

def get_party(link):
    party_elements = sub_url_partis(link).find_all("td", {"class": "overflow_name"})
    party_names = [party.get_text() for party in party_elements]
    return party_names

def get_town_codes(link):
    code_elements = url_catch(link).find_all("td", {"class": "cislo"})
    codes = [code.get_text() for code in code_elements]
    return codes

def get_votes(link):
    votes_list = []
    for url in get_codes_url(link):
        sub_soup = sub_url(url)
        votes_elements = sub_soup.find_all("td", {"class": "cislo"}, headers=["t1sb3", "t2sb3"])
        get_votes = [votes.get_text().replace("\xa0", "") for votes in votes_elements]
        votes_list.append(list(map(int, get_votes)))
    return votes_list

def main():
    link, csv_file_name = arg_parse()
    html_content = url_catch(link)
    if html_content is None:
        return

    print("Downloading...")

    header = ["code", "location", "registered", "envelopes", "valid"] + get_party(link)

    rows = [header]
    town_codes = get_town_codes(link)
    town_names = get_town_names(link)
    registered = get_registered(get_codes_url(link))
    envelopes = get_envelopes(get_codes_url(link))
    valid_votes = get_valid_votes(link)
    party_votes = get_votes(link)

    for i in range(len(town_names)):
        row = [town_codes[i], town_names[i], registered[i], envelopes[i], valid_votes[i]] + party_votes[i]
        rows.append(row)

    with open(csv_file_name, "w", newline="", encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

if __name__ == "__main__":
    main()
