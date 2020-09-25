import requests, bs4
from bs4 import BeautifulSoup as soup
import general
import time

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
availabilityTranslations = {'http://schema.org/OutOfStock': 'Out of stock', 'http://schema.org/PreOrder': 'Preorder', 'http://schema.org/InStock': 'In stock'}
urls = ['https://www.scan.co.uk/shop/computer-hardware/gpu-nvidia/nvidia-geforce-rtx-3080-graphics-cards','https://www.scan.co.uk/shop/computer-hardware/gpu-nvidia/nvidia-geforce-rtx-3090-graphics-cards']

def make_soup(url):
    r = requests.get(url, headers=headers)
    return soup(r.text, 'html.parser')

def get_product_data(product):
    try:
        d = {}
        d['name'] = product.find('span', {'class': 'description'}).contents[0].contents[0].strip()
        d['id'] = product['data-wpid']
        d['image'] = product.find('img')['src']
        d['url'] = f"https://scan.co.uk{product.find('span', {'class': 'description'}).find('a')['href']}"
        page = make_soup(d['url'])
        d['availability'] = availabilityTranslations[page.find('link', {'itemprop': 'availability'})['href']]
        d['price'] = page.find('span', {'itemprop': 'price'})['content']
        d['priceCurrency'] = page.find('span', {'itemprop': 'priceCurrency'})['content']
        return d
    except:
        time.sleep(150)
        return get_product_data(product)

while True:
    for url in urls:
        page = make_soup(url)
        productData = [get_product_data(i) for i in page.find_all('li', {'class': 'product'})]
        for product in productData:
            prevState = general.get_prev_state('scan', product['id'])
            general.update_db('scan', product)
            if prevState == None:
                continue
            elif prevState['price'] == product['price'] and prevState['availability'] == product['availability']:
                continue
            else:
                general.notify(product, prevState)
    time.sleep(general.waitInterval)