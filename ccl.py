import requests, bs4
from bs4 import BeautifulSoup as soup
import general

# We're using iPhone headers this time bois
headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
urls = ['https://m.cclonline.com/category/430/PC-Components/Graphics-Cards/GeForce-RTX-3080-Graphics-Cards/']

def make_soup(url):
    r = requests.get(url, headers=headers)
    return soup(r.text, 'html.parser')

def get_product_data(product):
    d = {}
    d['name'] = product.find('img')['alt']
    d['url'] = f"https://cclonline.com{product.find('a', {'class': 'producturl'})['href']}"
    d['id'] = make_soup(d['url']).find('span', {'itemprop': 'sku'}).contents[0]
    d['image'] = f"https://m.cclonline.com/{product.find('img')['src']}"
    availability = product.find('div', {'class': 'ProductListingStockInfo'})
    if 'green' in ''.join([''.join(i['class']) for i in availability.find_all(True)]):
        d['availability'] = 'In stock'
    elif 'blue' in ''.join([''.join(i['class']) for i in availability.find_all(True)]):
        d['availability'] = 'Out of stock'
    d['price'] = product.find('span', {'class': 'price-text-medium'}).contents[0].strip('£')
    return d

for url in urls:
    page = make_soup(url)
    productData = [get_product_data(i) for i in page.find('div', {'class': 'product-listing-container'}).find_all('div', {'class': 'product-listing'})]
    for product in productData:
        prevState = general.get_prev_state('ccl', product['id'])
        general.update_db('ccl', product)
        if prevState == None:
            continue
        elif prevState['price'] == product['price'] and prevState['availability'] == product['availability']:
            continue
        else:
            general.notify(product, prevState)