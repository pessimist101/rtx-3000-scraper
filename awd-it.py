import requests, bs4
from bs4 import BeautifulSoup as soup
import general
import re

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
urls = ['https://www.awd-it.co.uk/components/graphics-cards/nvidia/nvidia-geforce-rtx-3080.html']

def make_soup(url):
    r = requests.get(url, headers=headers)
    return soup(r.text, 'html.parser')

def get_product_data(product):
    d = {}
    d['name'] = product.find('a', {'class': 'product-title'})['title']
    d['url'] = product.find('a', {'class': 'product-title'})['href']
    d['id'] = product.find('a', {'class': 'product-title'})['id'].split('det_img_')[1]
    d['image'] = product.find('img', {'class': 'primary'})['data-src']
    if product.find('span', {'class': 'ty-qty-out-of-stock'}): # Out of stock
        d['availability'] = 'Out of stock'
    elif product.find('a', {'title': 'Add to Basket'}): # In stock
        d['availability'] = 'In stock'
    d['price'] = product.find('span', {'class': 'ty-price-num'}).contents[0]
    return d

while True:
    for url in urls:
        page = make_soup(url)
        productList = page.find('div', {'class': 'grid-list vs-grid-table-wrapper'}).find_all('div', {'class': 'ty-column4'})
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
    time.sleep(general.waitInterval)