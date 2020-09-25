import requests, bs4
from bs4 import BeautifulSoup as soup
import general
import time

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
availabilityTranslations = {'homeDeliveryUnavailable': 'Out of stock', 'homeDeliveryAvailable': 'In stock', 'nostock': 'Out of stock'}
urls = ['https://www.currys.co.uk/gbuk/search-keywords/xx_xx_30343_xx_xx/rtx%2B3080/xx-criteria.html', 'https://www.currys.co.uk/gbuk/search-keywords/xx_xx_xx_xx_xx/rtx%2B3090/xx-criteria.html']

def make_soup(url):
    r = requests.get(url, headers=headers)
    return soup(r.text, 'html.parser')

def get_product_data(product):
    try:
        d = {}
        brand = product.find('span', {'data-product': 'brand'}).contents[0]
        d['name'] = f"{brand} {product.find('span', {'data-product': 'name'}).contents[0]}"
        d['id'] = product['id'].strip('product')
        d['image'] = product.find('picture')['data-iesrc']
        d['url'] = product.find('a')['href']
        d['price'] = product.find('strong', {'class': 'price', 'data-product': 'price'}).contents[0].strip().strip('£')
        try:
            d['availability'] = availabilityTranslations[product.find('ul', {'data-product': 'availability'}).find('li')['data-availability']]
        except KeyError:
            d['availability'] = availabilityTranslations[product.find('ul', {'data-product': 'availability'}).find('li')['class'][0]]
        return d
    except:
        time.sleep(150)
        return get_product_data(product)

while True:
    for url in urls:
        page = make_soup(url)
        productList = page.find('div', {'class': 'col12 resultList', 'data-component': 'product-list-view'}).find_all('article')
        productData = [get_product_data(i) for i in productList]
        for product in productData:
            prevState = general.get_prev_state('currys', product['id'])
            general.update_db('currys', product)
            if prevState == None:
                continue
            elif prevState['price'] == product['price'] and prevState['availability'] == product['availability']:
                continue
            else:
                general.notify(product, prevState)
    time.sleep(general.waitInterval)