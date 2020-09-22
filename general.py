import requests
import json

with open('config.json', 'r') as f:
    webhookUrl = json.load(f.read())['webhookUrl']

def notify(product: dict, prevState: dict):
    message = compare(product, prevState)
    embed = make_embed(product, message)
    requests.post(webhookUrl, payload)

def make_embed(product: dict, message: str):
    embed = {
        "content": "A card is back in stock!",
        "embeds": [
            {
                "author": {
                    "name": product['name'],
                    "url": product['url'],
                    "icon_url": product['url']
                },
                "description": message,
                "thumbnail": {
                    "url": product['image']
                }
            }
        ]
    }
    return embed

def get_prev_state(db: str, id: str):
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute(f"SELECT id, price, availability FROM {db} WHERE id='{id}'")
    r = c.fetchall()
    if len([item for tup in r for item in tup]) > 0:
        return [{'id': i[0], 'price': i[1], 'availability': i[2]} for i in r][0]
    else:
        return None

def compare(new: dict, old: dict):
    m = []
    if new['price'] > old['price']:
        m.append(f"Price has gone up! Was {old['price']}, now {new['price']}")
    elif new['price'] < old['price']:
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
    message = '\n'e.join(m) if len(m) > 0 else None
    return message
