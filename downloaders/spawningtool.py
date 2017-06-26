""" Download & parse spawningtool build orders """

from __future__ import print_function

import glob
import os
from urlparse import urlparse, urljoin, urlsplit

from bs4 import BeautifulSoup
import requests

import sc2_build_order as sc2bo


def main():
    existing_urls = set([b.url for b in load_builds('../data/builds/*.json')])
    link = 'http://lotv.spawningtool.com/build/zvx/?name=&contributor=&sort_by=t&build_type=&patch=&mine=&fav='
    download_builds(link, 'data/builds', existing_urls)


def load_builds(glob_pattern):
    for path in glob.glob(glob_pattern):
        yield sc2bo.from_json(path)


def download_builds(url, to_dir, existing_build_urls=None):
    """ Download all builds found at the given url 
    
    Parameters
        url:                 url to find & download builds from
        to_dir:              dir to save builds to
        existing_build_urls: if not None, exclude existing builds based on url
    """
    for spawning_tool_build in find_spawningtool_builds(url):
        if spawning_tool_build.url in existing_build_urls:
            print('skipping ' + spawning_tool_build.url)
            continue
        print('downloading ' + spawning_tool_build.url)
        filename = url_to_filename(spawning_tool_build.url, 'json')
        out_path = os.path.join(to_dir, filename)
        try:
            spawning_tool_build.download_build(out_path)
        except Exception as e:
            print('    error: ' + str(e))


def find_spawningtool_builds(file_or_url):
    """ Returns list of SpawningToolBuild from the given html """
    urlroot = get_url_root(file_or_url) if is_url(file_or_url) else None
    html = load_html(file_or_url)
    soup = BeautifulSoup(html, 'html.parser')
    for row in soup.find_all('tr'):
        cols = row.find_all('td')
        name = unicode(cols[1].b.a.string)
        link = cols[1].b.a['href']
        matchup = unicode(cols[2].string)
        category = unicode(cols[3].string)
        race = 'Terran' if matchup[0] == 'T' else 'Protoss' if matchup[0] == 'P' else 'Zerg'
        if not is_url(link):
            link = urljoin(urlroot, link)
        yield SpawningToolBuild(name, link, race, category)


def html_to_build_order(html, url=None, race=None, category=None):
    """ Converts spawningtool html to a BuildOrder """
    soup = BeautifulSoup(html, 'html.parser')
    name = str(soup.find('h1').string)
    build_order = sc2bo.BuildOrder(name, race, url, category)

    build_table = soup.find(id="build-1")
    for row in build_table.find_all('tr'):
        cols = row.find_all('td')
        supply = unicode(cols[0].string)
        time = unicode(cols[1].string)
        unit = unicode(row.find('span').string)
        build_order.steps.append(sc2bo.BuildStep(supply, 0, unit, time))

    return build_order


class SpawningToolBuild:
    def __init__(self, name, url, race, category):
        self.name = name
        self.url = url
        self.race = race
        self.category = category

    def download_build(self, to_path):
        html = load_html(self.url)
        bo = html_to_build_order(html, self.url, self.race, self.category)
        bo.to_json(to_path)

    def __str__(self):
        return u'{}, {}, {}, {}'.format(self.name, self.race, self.category, self.url)


def is_url(path):
    return 'http://' in path or 'https://' in path


def load_html(path):
    """ Load html from a url or file path """
    if is_url(path):
        result = requests.get(path)
        return result.content
    # else
    with open(path) as html_file:
        return html_file.read()


def get_url_root(url):
    parsed_url = urlparse(url)
    return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)


def url_to_filename(url, ext):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.replace(':', '.')
    if netloc.endswith('.'):
        netloc = netloc[:-1]
    path = parsed_url.path.replace('/', '.')
    if path.endswith('.'):
        path = path[:-1]
    return '{}.{}.{}'.format(netloc, path, ext)


if __name__ == '__main__':
    main()
