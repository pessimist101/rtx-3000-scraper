import requests, bs4
from bs4 import BeautifulSoup as soup
import general

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
urls = ['https://www.aria.co.uk/Products?search=3080&x=0&y=0']

def make_soup(url):
    r = requests.get(url, headers=headers)
    return soup(r.text, 'html.parser')

def get_product_data(product):
    d = {}
    d['name'] = product.find_all('td')[1].find('a').contents[0]
    d['url'] = f"https://aria.co.uk{product.find('a')['href']}"
    d['id'] = d['url'].strip('?productId=')[1].strip('&')[0]
    page = make_soup(d['url'])
    page = page.find('table', {'class': 'fBox'})
    d['image'] = page.find('img')['src']
    availability = [i for i in page.find_all('td', {'class': 'colLeftR'}) if i.contents[0] == 'Stock:'][0]
    if availability.parent.find('td', {'class': 'colRight'}).find('strong') is None:
        d['availability'] = 'In stock' if 'in stock' in availability.parent.find('img')['alt'].lower() else 'Out of stock'
    else:
        d['availability'] = availability.parent.find('td', {'class': 'colRight'}).find('strong').contents[0].strip('!')[0]
    d['price'] = product.find_all('td')[-2].find('span', {'class': 'price bold'}).contents[0].strip('£')[0]
    return d

for url in urls:
    page = make_soup(url)
    productTable = page.find('table', {'class':'listTable'})
    products = productTable.find_all('tr', {'class': 'listTableTr'})
    productData = [get_product_data(i) for i in products]
    for product in productData:
        prevState = general.get_prev_state('ariapc', product['id'])
        general.update_db('ariapc', product)
        if prevState == None:
            continue
        elif prevState['price'] == product['price'] and prevState['availability'] == product['availability']:
            continue
        else:
            general.notify(product, prevState)