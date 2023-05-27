
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd


def scrape_product_list(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        products = soup.find_all(
            'div', {'data-component-type': 's-search-result'})
        data = []

        for product in products:
            product_url = 'https://www.amazon.in' + \
                product.find(
                    'a', {'class': 'a-link-normal a-text-normal'})['href']
            product_name = product.find(
                'span', {'class': 'a-size-medium a-color-base a-text-normal'}).text.strip()
            product_price = product.find(
                'span', {'class': 'a-offscreen'}).text.strip()
            product_rating = product.find(
                'span', {'class': 'a-icon-alt'}).text.strip().split(' ')[0]
            product_reviews = product.find(
                'span', {'class': 'a-size-base'}).text.strip().replace(',', '')

            data.append([product_url, product_name, product_price,
                        product_rating, product_reviews])

        return data
    else:
        print(
            f"Failed to retrieve page {url}. Status code: {response.status_code}")
        return []


def scrape_product_details(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        product_description = soup.find('div', {'id': 'productDescription'})
        if product_description:
            product_description = product_description.text.strip()
        else:
            product_description = ''

        product_asin = soup.find(
            'th', {'class': 'a-color-secondary a-size-base prodDetSectionEntry'})
        if product_asin:
            product_asin = product_asin.text.strip()
        else:
            product_asin = ''

        product_manufacturer = soup.find('a', {'id': 'bylineInfo'})
        if product_manufacturer:
            product_manufacturer = product_manufacturer.text.strip()
        else:
            product_manufacturer = ''

        return product_description, product_asin, product_manufacturer
    else:
        print(
            f"Failed to retrieve product URL {url}. Status code: {response.status_code}")
        return '', '', ''


base_url = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_'
all_data = []

for page_number in range(1, 21):
    url = base_url + str(page_number)
    try:
        data = scrape_product_list(url)
        if data:
            all_data.extend(data)
        time.sleep(2)  # Add a delay of 2 seconds between requests
    except Exception as e:
        print(f"Failed to scrape page {page_number}: {e}")

for i, product_data in enumerate(all_data):
    url = product_data[0]
    try:
        description, asin, manufacturer = scrape_product_details(url)
        all_data[i].extend([description, asin, manufacturer])
        time.sleep(2)  # Add a delay of 2 seconds between requests
    except Exception as e:
        print(f"Failed to scrape product URL {url}: {e}")

df = pd.DataFrame(all_data, columns=['Product URL', 'Product Name', 'Product Price',
                  'Rating', 'Number of Reviews', 'Description', 'ASIN', 'Manufacturer'])
df.to_csv('product_data.csv', index=False)
