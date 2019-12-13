#!/usr/bin/python3

import numpy as np
import re
import json
import yaml

from datetime import datetime

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def parse_fares(soup):
    fares = soup.find_all('span', attrs={'class': 'fareOutput'})
    f = [float(fare.get_text()[:-4].replace(',', '.')) for fare in fares]

    return f


def parse_departure_times(soup):
    times = soup.find_all('td', attrs={'class': 'time'})
    t = [re.sub('\W+','', ':'.join(time.get_text().split(':')[:2])) for time in times]

    return t


def parse_num_changes(soup):
    changes = soup.find_all('td', attrs={'class': 'changes lastrow'})
    ch = [re.sub('\W+','', c.get_text()) for c in changes]

    return ch


def parse_connections(soup):
    cons = soup.find_all('tbody', attrs={'class': 'boxShadow scheduledCon'})
    return cons


def parse_page(soup):
    connections = parse_connections(soup)
    c = []
    for connection in connections:
        d = {'time': parse_departure_times(connection)[:2],
             'changes': parse_num_changes(connection),
             'fare': parse_fares(connection)[0]}
        
        c.append(d)

    return c


def read_connections_from_yaml(filename):
    dicts = []

    with open(filename) as file:
        connections = yaml.full_load(file) 

        for entries in connections:
            dicts.append(entries[list(entries.keys())[0]])

    return dicts


if __name__ == "__main__":
    connection_dicts = read_connections_from_yaml('connections.yaml')

    for c in connection_dicts:
        raw_html = simple_get(c['url'])
        #raw_html = open('tmp.txt').read()
        soup = BeautifulSoup(raw_html, 'html.parser')

        connection_dict = parse_page(soup)
        connection_dict_json = json.dumps(connection_dict)

        now = datetime.now() # current date and time
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

        name = '{0}_{1}.txt'.format(c["connection_name"], c["date"])
        f = open(name, "a+")
        f.write(date_time + ': ')
        f.write(connection_dict_json)
        f.write('\n')
