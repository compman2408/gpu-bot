#!/usr/bin/env python3

import sys
import time
import requests
import argparse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from bs4 import BeautifulSoup


class TextColors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
    @staticmethod
    def print_red(text_to_print):
        print(f'{TextColors.RED}{text_to_print}{TextColors.RESET}')

    @staticmethod
    def print_green(text_to_print):
        print(f'{TextColors.GREEN}{text_to_print}{TextColors.RESET}')

    @staticmethod
    def print_yellow(text_to_print):
        print(f'{TextColors.YELLOW}{text_to_print}{TextColors.RESET}')


class BestBuyWatcher:
    DEFAULT_HEADERS = {
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0',
        "origin": "https://www.bestbuy.com",
    }
    BBY_PRODUCT_URL = 'https://www.bestbuy.com/site/-/{sku}.p?cmp=RMX'
    BBY_ADD_TO_CART_URL = 'https://api.bestbuy.com/click/5592e2b895800000/{sku}/cart'
    SKUS_3090 = [
        '6432657',
        '6430215',
        '6432656',
        '6432447',
        '6436192',
        '6432446',
        '6437910',
        '6436193',
        '6445108',
        '6430623',
        '6434198',
        '6430624',
        '6429434',
    ]
    SKUS_3080 = [
        '6432658',
        '6430175',
        '6432655',
        '6432445',
        '6436223',
        '6436196',
        '6436219',
        '6436191',
        '6432400',
        '6430620',
        '6436194',
        '6430621',
        '6432399',
        '6429440',
    ]
    SKUS_3070 = [
        '6438278',
        '6439127',
        '6432654',
        '6432653',
        '6439301',
        '6439128',
        '6439384',
        '6439299',
        '6439385',
        '6437909',
        '6439300',
        '6437912',
        '6429442',
    ]


    def watch(self, card):
        if card == '3070':
            skus_to_watch = self.SKUS_3070
        elif card == '3080':
            skus_to_watch = self.SKUS_3080
        elif card == '3090':
            skus_to_watch = self.SKUS_3090
        else:
            print('Not a recognized card to watch. Aborting watcher...')
            sys.exit(1)

        with requests.Session()as bb_s:
            bb_s.headers.update(self.DEFAULT_HEADERS)

            adapter = HTTPAdapter(
                max_retries=Retry(
                    total=3,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                    method_whitelist=['HEAD', 'GET', 'OPTIONS', 'POST'],
                )
            )
            bb_s.mount('https://', adapter)
            bb_s.mount('http://', adapter)

            while len(skus_to_watch) > 0:
                for cur_sku in skus_to_watch:
                    try:
                        bb_response = bb_s.get(self.BBY_PRODUCT_URL.format(sku=cur_sku))

                        if bb_response.status_code == 200:
                            soup = BeautifulSoup(bb_response.content, 'html.parser')
                            title = soup.title.text
                            cart_button_text = soup.body.find('button', attrs={'type':'button', 'class':'add-to-cart-button'}).text.lower()
                            price = soup.body.find('div', attrs={'class':'priceView-hero-price priceView-customer-price'}).text.lower()
                            price = soup.body.find('div', attrs={'class':'priceView-hero-price priceView-customer-price'}).find('span').text.lower()
                            if cart_button_text == 'add to cart':
                                TextColors.print_green('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                                TextColors.print_green('------------------------------')
                                TextColors.print_green("IT'S AVAILABLE!!!!!")
                                TextColors.print_green('')
                                TextColors.print_green(f'Product URL: "{bb_response.url}"')
                                TextColors.print_green(f'Page Title: "{soup.title.text}"')
                                TextColors.print_green(f'Product Price: "{price}"')
                                TextColors.print_green(f'Availability: {cart_button_text}')
                                TextColors.print_green("IT'S AVAILABLE!!!!!")
                                TextColors.print_green('')
                                TextColors.print_green('------------------------------')
                                TextColors.print_green('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                            elif cart_button_text in ['sold out', 'coming soon']:
                                TextColors.print_red(f'Product: {title}')
                                TextColors.print_red(f'Price: {price}')
                                TextColors.print_red(f'Availability: {cart_button_text}')
                            else:
                                TextColors.print_yellow(f'Product: {title}')
                                TextColors.print_yellow(f'Price: {price}')
                                TextColors.print_yellow(f'Availability: {cart_button_text}')
                        else:
                            print('Error!')
                            print(f'Response Code: "{bb_response.status_code}"')
                    except Exception as ex:
                        print(f'There was a booboo...{ex}')
                    
                    print('----------------------------')

                    # We don't want to get our IP blocked so let's not send 1,000,000 requests every minute
                    time.sleep(2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--card',
        required=True,
        choices=['3070', '3080', '3090'],
        help='Which card the script should watch for. For example, 3070, 3080, etc.'
    )

    args = parser.parse_args()
    print(f'Watching BestBuy for card: "{args.card}"')
    bbw = BestBuyWatcher()
    bbw.watch(args.card)
