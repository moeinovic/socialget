from pprint import pprint
from twittic import TwitterAPI

proxy = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}


API = TwitterAPI(proxies=proxy)

pprint(API.get_status("1542761898084532225"))