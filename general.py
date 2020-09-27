import requests
import json
import time
import sqlite3

with open('config.json', 'r') as f:
    config = json.load(f)
webhookUrl = config['webhookUrl']
waitInterval = config['waitInterval']

def notify(product: dict, prevState: dict):
    return
    message = compare(product, prevState)
    payload = make_message(product, message)
    requests.post(webhookUrl, payload)

def make_message(product: dict, msg: str):
    message = {}
    message['username'] = "RTX Bot"
    message['avatar_url'] = "https://www.manli.com/upload/2020/05/26/s[1]_ch5itbcpjef651590480885.png"
    message['embeds'] = []
    embed = {}
    embed['author'] = {"name": product['name'], "url": product['url']}
    embed['description'] = msg
    embed['thumbnail'] = {"url": product['image']}
    message['embeds'].append(embed)
    return message

def get_prev_state(retailer: str, id: str):
    conn = sqlite3.connect('/db/products.db')
    c = conn.cursor()
    c.execute(f"SELECT retailer, id, price, image, url, availability, time FROM products WHERE id='{id}' ORDER BY time DESC;")
    r = c.fetchone()
    c.close()
    type(r)
    if r == None or len(r) == 0:
        return None
    elif len(r) > 0:
        return {'id': r[0], 'price': r[1], 'availability': r[2]}

def compare(new: dict, old: dict):
    m = []
    if float(new['price']) > old['price']:
        m.append(f"Price has gone up! Was {old['price']}, now {new['price']}")
    elif float(new['price']) < old['price']:
        m.append(f"Price has gone down! Was {old['price']}, now {new['price']}")
    else:
        pass
    if new['availability'] == old['availability']:
        pass
    elif new['availability'] == 'In stock':
        m.append('Back in stock!')
    elif new['availability'] == 'Preorder':
        m.append('Now available for preorder!')
    elif new['availability'] == 'Out of stock':
        m.append('Out of stock :(')
    message = '\n'.join(m) if len(m) > 0 else None
    return message

def update_db(retailer: str, product: dict):
    conn = sqlite3.connect('/db/products.db')
    c = conn.cursor()
    product['retailer'] = retailer
    values = [product[i] for i in ['name', 'retailer', 'id', 'price', 'image', 'url', 'availability']]
    values.append(int(time.time()))
    values = str(tuple(values))
    c.execute(f"INSERT INTO products (name, retailer, id, price, image, url, availability, time) VALUES {values}")
    conn.commit()
    conn.close()