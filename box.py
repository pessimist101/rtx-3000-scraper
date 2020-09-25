import requests, bs4
from bs4 import BeautifulSoup as soup
import general
import time

# We're using iPhone headers this time bois
headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
availabilityTranslations = {'Coming Soon': 'Out of stock', 'Add To Basket': 'In stock'}
urls = ['https://www.box.co.uk/rtx-3080-graphics-cards','https://www.box.co.uk/rtx-3090-graphics-cards']

def make_soup(url):
    r = requests.get(url, headers=headers)
    return soup(r.text, 'html.parser')

def get_product_data(product):
    try:
        d = {}
        d['name'] = product.find('h3').find('a').contents[0]
        d['url'] = product.find('h3').find('a')['href']
        d['id'] = product.find('p', {'class': 'p-list-manufacturercode'}).contents[0]
        d['image'] = f"https://www.box.co.uk{product.find('img')['data-src']}"
        availability = product.find(True, {'class': 'p-list-add'})
        if availability.find('a') != None: # In stock
            d['availability'] = availabilityTranslations[availability.find('a').contents[0]]
        else:
            d['availability'] = availabilityTranslations[availability.contents[0]]
        d['price'] = product.find('span', {'class': 'pq-price'})['data-inc'].strip('£')
        return d
    except:
        time.sleep(150)
        return get_product_data(product)

while True:
    for url in urls:
        page = make_soup(url)
        productData = [get_product_data(i) for i in page.find('div', {'class': 'product-list'}).find_all('div', {'class': 'product-list-item'})]
        for product in productData:
            prevState = general.get_prev_state('box', product['id'])
            general.update_db('box', product)
            if prevState == None:
                continue
            elif prevState['price'] == product['price'] and prevState['availability'] == product['availability']:
                continue
            else:
                general.notify(product, prevState)
    time.sleep(general.waitInterval)