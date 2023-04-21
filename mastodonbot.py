import os
import requests
import time
import mastodon
from mastodon import Mastodon

COINS = [
    'bitcoin', 'ethereum', 'solana', 
    'binancecoin', 'cardano', 'monero', 
    'litecoin','dogecoin'
]

API_BASE_URL = "https://mastodon.social"

INTERVAL = 'daily'
SLEEP_BETWEEN_POST = 1
SLEEP_PREVENT_TOO_MANY_REQUESTS = 6


def create_api():
    api = Mastodon(
        access_token=os.environ['ACCESS_TOKEN'], 
        api_base_url=API_BASE_URL
    )
    return api

def get_price_last_hour(coin, interval):
    response = requests.get(
        f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=0&interval={interval}"
    ).json()
    price_last_hour = response['prices'][0][1]
    return price_last_hour

def get_price(coin):
    response = requests.get(
        f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    )
    return response.json()[f"{coin}"]['usd']

def generate_status(coin, price, price_1h, interval):
    price_change = round(price - price_1h, 2)
    change_percent = round(((price/price_1h) * 100) - 100, 2)

    emoji = "🔴⬇️" if change_percent < 0 else "🟢⬆️"

    status = (
        f"#{coin} Stats 📊📈📉 (last {interval})\n\n" \
        f"Price: {price} USD💵\n" \
        f"Variation: {change_percent}% ({price_change} USD💵) {emoji}"
    )

    return status

def post_status(api, status):
    try:
        api.toot(status)
        print("status updated")
    except Exception as e:
        print("error ~> ", e)

def main():    
    api = create_api()

    for coin in COINS:
        price = float(get_price(coin))
        time.sleep(SLEEP_PREVENT_TOO_MANY_REQUESTS) # sleep necessary to prevent 429 Too Many Requests error.
        price_1h = float(get_price_last_hour(coin, INTERVAL))

        status = generate_status(coin, price, price_1h, INTERVAL)

        post_status(api, status)

        time.sleep(SLEEP_BETWEEN_POST)

if __name__ == '__main__':
    main()