import sqlite3
import urllib.request
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self, site):
        self.site = site
        self.links = set()
        self.celebs = {}
        self.conn = sqlite3.connect("my.db")

    def create_database(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS celebs 
                    (name text, networth int)''')

    def close_database(self):
        self.conn.close()

    def get_links(self, number_of_pages):
        for i in range(1, number_of_pages):
            if i == 1:
                r = urllib.request.urlopen(self.site)
            else:
                r = urllib.request.urlopen(self.site + "page/" + str(i))
            soup = BeautifulSoup(r.read(), "html.parser")
            for a in soup.find_all('a', href=True):
                link = a['href']
                if '-net-worth/' in link:
                    self.links.add(link)
            print(self.links)

    def scrape_networth(self, number_of_pages):
        self.get_links(number_of_pages)
        for link in self.links:
            r = urllib.request.urlopen(link)
            soup = BeautifulSoup(r.read(), "html.parser")
            try:
                self.celebs[soup.findAll("div", {"class": "title"})[0].text] = soup.findAll("div", {"class": "value"})[0].text
            except IndexError:
                pass

        print(self.celebs)
        for name, networth in self.celebs.items():
            params = (name, networth)
            self.conn.execute("INSERT INTO celebs VALUES (?, ?)", params)

        self.conn.commit()

    def get_networth(self, name):
        name += " net worth:"
        c = self.conn.cursor()
        c.execute("SELECT * FROM celebs WHERE name=?", (name,))
        print(c.fetchone())

scrape = Scraper('https://www.celebritynetworth.com/category/richest-celebrities/')
scrape.create_database()
scrape.scrape_networth(3)
scrape.get_networth("Elton John")
scrape.close_database()
