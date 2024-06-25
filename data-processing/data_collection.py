import httpx
import asyncio
import random
import csv
import os
import json
from tqdm import tqdm
from bs4 import BeautifulSoup
import re
import time

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:85.0) Gecko/20100101 Firefox/85.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
]

CONCURRENCY = 50  # Set the number of concurrent requests


async def fetch(url, session, semaphore, retries=3):
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': 'https://www.cian.ru/',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }
    async with semaphore:
        for attempt in range(retries):
            try:
                res = await session.get(url, headers=headers, timeout=10)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')

                    title_container = soup.find('div', {'data-name': 'OfferTitleNew'})
                    title = title_container.find('h1').text.strip() if title_container else None

                    price_div = soup.find('div', {'data-testid': 'price-amount'})
                    price_span = price_div.find('span') if price_div else None
                    price = int(re.sub(r'\D', '', price_span.text.strip())) if price_span else None

                    address_container = soup.find('div', {'data-name': 'AddressContainer'})
                    address_parts = address_container.find_all('a', {
                        'data-name': 'AddressItem'}) if address_container else []
                    address = ', '.join([part.text.strip() for part in address_parts])

                    price_per_meter_div = soup.find('div', {'data-name': 'OfferFactItem'})
                    price_per_meter_label = price_per_meter_div.find('span',
                                                                     string='Цена за метр') if price_per_meter_div else None
                    price_per_meter_span = price_per_meter_label.find_next('span') if price_per_meter_label else None
                    price_per_meter = re.sub(r'\D', '',
                                             price_per_meter_span.text.strip()) if price_per_meter_span else None

                    housing_type = None
                    total_area = None
                    kitchen_area = None
                    ceiling_height = None
                    renovation = None
                    construction_year = None

for info_item in soup.find_all('tr', {'data-name': 'OfferSummaryInfoItem',
                                                          'data-testid': 'OfferSummaryInfoItem'}):
                        label = info_item.find('p', class_='a10a3f92e9--color_gray60_100--mYFjS')
                        value = info_item.find('p', class_='a10a3f92e9--color_black_100--Ephi7')
                        if label and value:
                            label_text = label.text.strip()
                            value_text = value.text.strip()
                            if label_text == 'Тип жилья':
                                housing_type = value_text
                            elif label_text == 'Общая площадь':
                                total_area = value_text
                            elif label_text == 'Площадь кухни':
                                kitchen_area = value_text
                            elif label_text == 'Высота потолков':
                                ceiling_height = value_text
                            elif label_text == 'Ремонт':
                                renovation = value_text
                            elif label_text == 'Год постройки':
                                construction_year = value_text

                    floor = None
                    factoids = soup.find_all('div', {'data-name': 'ObjectFactoidsItem'})
                    for factoid in factoids:
                        label = factoid.find('span', class_='a10a3f92e9--color_gray60_100--mYFjS')
                        if label and 'Этаж' in label.text:
                            value_span = factoid.find('span', class_='a10a3f92e9--color_black_100--Ephi7')
                            floor = value_span.text.strip() if value_span else None
                            break

                    seller_info_div = soup.find('div', {'data-name': 'AuthorAside'})
                    seller_type_span = seller_info_div.find('span',
                                                            class_='a10a3f92e9--color_black_100--Ephi7') if seller_info_div else None
                    seller_type = seller_type_span.text.strip() if seller_type_span else None

                    if not (title and price and address):
                        print(f'Incomplete data for URL: {url}')
                        return None

                    return {
                        'url': url,
                        'title': title,
                        'price': price,
                        'address': address,
                        'price_per_meter': price_per_meter,
                        'housing_type': housing_type,
                        'total_area': total_area,
                        'kitchen_area': kitchen_area,
                        'ceiling_height': ceiling_height,
                        'renovation': renovation,
                        'construction_year': construction_year,
                        'floor': floor,
                        'seller_type': seller_type
                    }
                elif res.status_code == 403:
                    print(f'403 Forbidden for URL: {url}. Retrying after delay...')
                    await asyncio.sleep(random.uniform(10, 11))  # Increasing delay for retry
                else:
                    print(f'Failed to retrieve the page: {url} with status {res.status_code}')
                    return None
            except Exception as e:
                print(f'Exception while retrieving the page: {url}, error: {e}')
                await asyncio.sleep(random.uniform(10, 11))  # Increasing delay for retry
        return None


def save_to_csv(data, filename='data.csv'):
    if not data:
        print('No data to save.')
        return

    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)
    print(f'Successfully saved {len(data)} records to {filename}.')

async def main(urls):
    total_urls = len(urls)
    print(f'Total URLs to process: {total_urls}')

    semaphore = asyncio.Semaphore(CONCURRENCY)
    async with httpx.AsyncClient() as session:
        tasks = []
        all_data = []
        processed_count = 0

        for url in urls:
            tasks.append(fetch(url, session, semaphore))

            if len(tasks) >= 100:  # Batch processing to prevent memory overflow
                results = await asyncio.gather(*tasks)
                valid_results = [r for r in results if r]
                all_data.extend(valid_results)
                save_to_csv(valid_results)
                tasks = []

                processed_count += len(valid_results)
                print(f'Saved {processed_count} out of {total_urls} URLs')

                # Increasing delay between batches to prevent blocking
                await asyncio.sleep(random.uniform(4, 6))

        if tasks:
            results = await asyncio.gather(*tasks)
            valid_results = [r for r in results if r]
            all_data.extend(valid_results)

        if all_data:
            save_to_csv(all_data)
            print(f'Total saved records: {len(all_data)}')


if name == 'main':
    with open('listings.json', 'r', encoding='utf-8') as file:
        urls = json.load(file)
    print(f'Loaded {len(urls)} URLs')

    asyncio.run(main(urls))
