from os import getenv
from sys import argv
import requests
from pprint import pprint

BOT_TOKEN = getenv('BA_BOT_TOKEN')
tg_url = f'https://api.telegram.org/bot{BOT_TOKEN}'
bot_url = getenv('WEBHOOK_URL')

if argv[1] == 'set':
    tg_url += f'/setWebhook?url={bot_url}/{BOT_TOKEN}'
elif argv[1] == 'del':
    tg_url += '/deleteWebhook'
else:
    tg_url += '/getWebhookInfo'

r = requests.get(tg_url)
pprint(r.json())
