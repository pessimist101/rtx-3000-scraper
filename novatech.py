import requests, bs4
from bs4 import BeautifulSoup as soup
import general

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
availabilityTranslations = {'Very short supply, no confirmed date': 'Out of stock', 'In stock': 'In stock', 'Stock Due Today': 'Preorder', 'Ordered Upon Request': 'Preorder'}
urls = ['https://www.novatech.co.uk/products/components/nvidiageforcegraphicscards/nvidiartxseries/nvidiartx3080/']

def make_soup(url):
    r = requests.get(url, headers=headers)
    return soup(r.text, 'html.parser')

def get_product_data(product):
    d = {}
    d['name'] = product.find('img')['title'].strip()
    d['id'] = product.find('p', {'class': 'stockcodes'}).contents[0].split('Stock Code: ')[1]
    img = product.find('img')
    d['image'] = img['data-src'] if 'src' not in img.attrs else img['src']
    d['url'] = f"https://www.novatech.co.uk{product.find('a')['href']}"
    d['price'] = product.find('p', {'class': 'newspec-price-listing'}).contents[0].strip('£')
    availability = product.find('span', {'class': 'newspec-stock-status'}).contents[0].strip()
    if availability.lower().strip().endswith('in stock'):
        availability = 'In stock'
    d['availability'] = availabilityTranslations[availability]
    return d

for url in urls:
    page = make_soup(url)
    productList = page.find('div', {'class': 'col-xs-12 col-nopadding'}).contents
    productList = [i for i in productList if isinstance(i, bs4.element.Tag) and i.attrs['class'] == ['col-xs-12'] and 'id' not in i.attrs]
    productData = [get_product_data(i) for i in productList]
    for product in productData:
        prevState = general.get_prev_state('novatech', product['id'])
        general.update_db('novatech', product)
        if prevState == None:
            continue
        elif prevState['price'] == product['price'] and prevState['availability'] == product['availability']:
            continue
        else:
            general.notify(product, prevState)