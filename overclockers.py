import requests, bs4
from bs4 import BeautifulSoup as soup
import general
import re
import time

# We're using iPhone headers this time bois
headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
urls = ['https://www.overclockers.co.uk/pc-components/graphics-cards/nvidia/geforce-rtx-3080', 'https://www.overclockers.co.uk/pc-components/graphics-cards/nvidia/geforce-rtx-3080?p=2','https://www.overclockers.co.uk/pc-components/graphics-cards/nvidia/geforce-rtx-3090']

def make_soup(url):
    r = requests.get(url, headers=headers)
    return soup(r.text, 'html.parser')

def get_product_data(product):
    d = {}
    d['name'] = product.find('span', {'class': 'article-subtitle'}).contents[0].strip()
    d['url'] = product.find('a')['href']
    d['id'] = product.find('input', {'class': 'ArboroGoogleAnalyticsProductOrderNr'})['value']
    d['image'] = product.find('img')['src']
    productPage = make_soup(d['url'])
    availability = productPage.find('p', {'class': re.compile("deliverable[0-9]")})
    if availability == None: # Out of stock
        d['availability'] = 'Out of stock'
    elif availability.find('span') == None: # In Stock
        d['availability'] = availability.contents[0].split('\n')[-2]
    else: # Pre order
        d['availability'] = availability.find('span', {'class': 'frontend_plugins_index_delivery_informations'}).contents[0]
        d['availability'] = 'Preorder' if d['availability'] == 'Pre Order' else d['availability']
    d['price'] = product.find('span', {'class': 'price'}).contents[0].strip().strip('£')
    return d

while True:
    for url in urls:
        page = make_soup(url)
        productList = page.find('div', {'class': 'ck_listing article-listing clear'})
        productData = [get_product_data(i) for i in productList.find_all('article')]
        for product in productData:
            prevState = general.get_prev_state('overclockers', product['id'])
            general.update_db('overclockers', product)
            if prevState == None:
                continue
            elif prevState['price'] == product['price'] and prevState['availability'] == product['availability']:
                continue
            else:
                general.notify(product, prevState)
    time.sleep(general.waitInterval)