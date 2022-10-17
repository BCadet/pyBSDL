import requests
import os
from bs4 import BeautifulSoup

class bsdl_fetcher:
    BSDL_SITE = 'https://bsdl.info/'
    BSDL_SEARCH = BSDL_SITE + 'list.htm?search='

    def __init__(self):
        self.BSDL = {}
        self.search_result_list = {}

    def list_available_bsdl(self, IDCODE, discard_version=True):
        if discard_version :
            bsdl_search_link = '0000' + format(int(IDCODE), '032b')[4:]
        else:
            bsdl_search_link = format(int(IDCODE), '032b')
        
        page = requests.get(self.BSDL_SEARCH + bsdl_search_link)
        soup = BeautifulSoup(page.content, 'html.parser')
        panel = soup.select('div.panel')
        table = panel[0].select('table')
        entries = table[0].select('tbody')[0].select('tr')
        self.search_result_list[str(IDCODE)] = []
        for entry in entries:
            name = entry.select('td.text-left')[0].getText().strip()
            details = self.BSDL_SITE + entry.select('td.text-left')[0].select('a')[0].get('href')
            package = entry.select('td.text-left')[1].getText().strip()
            bsdl_link = self.BSDL_SITE + entry.select('a.button')[0].get('href')
            self.search_result_list[str(IDCODE)].append([name, package, details, bsdl_link])
        return self.search_result_list[str(IDCODE)]

    def fetch_bsdl(self, bsdl_link):
        page = requests.get(bsdl_link)
        soup = BeautifulSoup(page.content, 'html.parser')
        bsdl_full_name = soup.select('title')[0].getText().split()[0]
        self.BSDL[bsdl_full_name] = soup.select('code')[0].getText()
        return [bsdl_full_name, self.BSDL[bsdl_full_name]]

    def save_bsdl(self, bsdl_file_name, bsdl):
        with open(bsdl_file_name + '.bsd', 'wb') as f:
            f.write(bytearray(bsdl, 'UTF-8'))


if __name__ == '__main__':
    fetcher = bsdl_fetcher()
    list = fetcher.list_available_bsdl(0x06439041)
    bsdl_name, bsdl_file = fetcher.fetch_bsdl(list[0][3])
    fetcher.save_bsdl(bsdl_name, bsdl_file)