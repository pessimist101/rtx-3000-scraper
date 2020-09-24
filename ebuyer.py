import requests, bs4
from bs4 import BeautifulSoup as soup
import general
import time

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
availabilityTranslations = {'Add to Basket': 'In stock', 'Pre-order': 'Preorder'}
urls = ['https://www.ebuyer.com/store/Components/cat/Graphics-Cards-Nvidia/subcat/GeForce-RTX-3080']

def make_soup(url):
    r = requests.get(url, headers=headers)
    return soup(r.text, 'html.parser')

def get_product_data(product):
    d = {}
    d['name'] = product.find('img')['alt']
    d['id'] = product['data-product-id']
    d['image'] = product.find('img')['src']
    d['url'] = f"https://www.ebuyer.com{product.find('a')['href']}"
    if product.find('p', {'class':'price'}):
        d['price'] = product.find('p', {'class':'price'}).contents[2].strip()
    elif product.find('div', {'class': 'grid-item__price'}).contents[0].strip() == '':
        d['price'] = '0.00'
    if product.find('button', {'class': 'button--mini-basket'}): # In stock or Preorder
        d['availability'] = availabilityTranslations[product.find('button', {'class': 'button--mini-basket'}).contents[0]]
    else:
        d['availability'] = 'Out of stock'
    return d

while True:
    for url in urls:
        page = make_soup(url)
        productList = page.find('div', {'id': 'grid-view', 'class': 'grid-view js-taxonomy-view is-active'}).find_all('div', {'class': 'grid-item js-listing-product'})
        productData = [get_product_data(i) for i in productList]
        for product in productData:
            prevState = general.get_prev_state('ebuyer', product['id'])
            general.update_db('ebuyer', product)
            if prevState == None:
                continue
            elif prevState['price'] == product['price'] and prevState['availability'] == product['availability']:
                continue
            else:
                general.notify(product, prevState)
    time.sleep(general.waitInterval)