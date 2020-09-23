import requests, bs4
from bs4 import BeautifulSoup as soup

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}

def make_soup(url):
    r = requests.get(url, headers=headers)
    return soup(r.text, 'html.parser')

def get_prev_state(db, id):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute(f"SELECT id FROM {db} WHERE id IS '{id}'")
    results = c.fetchall()
    
