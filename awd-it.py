import requests, bs4
from bs4 import BeautifulSoup as soup
import general
import re
import time

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
urls = ['https://www.awd-it.co.uk/components/graphics-cards/nvidia/nvidia-geforce-rtx-3080.html','https://www.awd-it.co.uk/components/graphics-cards/nvidia/nvidia-geforce-rtx-3090.html']

def make_soup(url):
    r = requests.get(url, headers=headers)
    return soup(r.text, 'html.parser')

def get_product_data(product):
    d = {}
    try:
        d['name'] = product.find('a', {'class': 'product-title'})['title']
        d['url'] = product.find('a', {'class': 'product-title'})['href']
        d['id'] = product.find('img', {'class': 'ty-pict'})['id'].strip('det_img_')
        img = product.find('img', {'class': 'ty-pict'})
        d['image'] = img['data-src'] if 'data-src' in img.attrs else img['src']
        if product.find('span', {'class': 'ty-qty-out-of-stock'}): # Out of stock
            d['availability'] = 'Out of stock'
        elif product.find('a', {'title': 'Add to Basket'}): # In stock
            d['availability'] = 'In stock'
        d['price'] = product.find('span', {'class': 'ty-price-num'}).nextSibling.contents[0]
        return d
    except:
        time.sleep(150)
        return get_product_data(product)

while True:
    for url in urls:
        page = make_soup(url)
        productList = page.find('div', {'class': 'grid-list vs-grid-table-wrapper'}).find_all('div', {'class': 'ty-column4'})
        productData = [get_product_data(i) for i in productList if i.find('img') is not None]
        for product in productData:
            prevState = general.get_prev_state('awd-it', product['id'])
            general.update_db('awd-it', product)
            if prevState == None:
                continue
            elif prevState['price'] == product['price'] and prevState['availability'] == product['availability']:
                continue
            else:
                general.notify(product, prevState)
    time.sleep(general.waitInterval)