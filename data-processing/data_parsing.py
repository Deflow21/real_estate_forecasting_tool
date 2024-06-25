from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

MAX_LISTINGS = 1700
INCREASE_STEP = 100000
INITIAL_STEP = 100000

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver
    except Exception as e:
        print(f"Error setting up the driver: {e}")
        return None

def parsed_url(html):
    soup = BeautifulSoup(html, 'html.parser')
    listings = soup.find_all('a', class_='_93444fe79c--link--VtWj6')
    parsed_url = [{'urls': listing.get('href')} for listing in listings]
    return parsed_url

def extract_num_listings(content):
    soup = BeautifulSoup(content, 'html.parser')
    summary_header = soup.find('div', {'data-name': 'SummaryHeader'})
    if summary_header:
        h5 = summary_header.find('h5')
        if h5:
            text = h5.text.strip()
            num_listings = int(''.join([s for s in text.split() if s.isdigit()]))
            return num_listings
    return 0

def get_num_listings_for_range(driver, base_url, min_price, max_price):
    url = f"{base_url}&minprice={min_price}&maxprice={max_price}"
    driver.get(url)
    time.sleep(1)
    content = driver.page_source
    num_listings = extract_num_listings(content)
    return num_listings

def scrape_all_pages(driver, base_url, min_price, max_price):
    all_listings = []
    page = 1
    while True:
        url = f"{base_url}&minprice={min_price}&maxprice={max_price}&p={page}"
        driver.get(url)
        time.sleep(3)

        print(f"Парсинг страницы {page} для диапазона цен {min_price}-{max_price}")

        content = driver.page_source
        listings = parsed_url(content)
        if not listings:
            print(f"Нет объявлений на странице {page}, прекращаем обработку.")
            break

        all_listings.extend(listings)
        print(f"Добавлено {len(listings)} объявлений с страницы {page}")

        try:
            next_button = driver.find_elements(By.XPATH, "//a[contains(@class, '_93444fe79c--button--KVooB') and span[text()='Дальше']]")
            if not next_button:
                print(f"Кнопка 'Дальше' отсутствует на странице {page}. Завершаем парсинг.")
                break
        except:
            print(f"Ошибка при проверке наличия кнопки 'Дальше'. Завершаем парсинг.")
            break

        page += 1

    return all_listings

def filter_by_price(base_url, start_price, end_price, step):
    driver = setup_driver()
    if not driver:
        return []

    all_listings = []
    current_min_price = start_price
    try:
        while current_min_price < end_price:
            current_max_price = current_min_price + step
            num_listings = get_num_listings_for_range(driver, base_url, current_min_price, current_max_price)
            while num_listings < MAX_LISTINGS and current_max_price < end_price:
                print(f"Недостаточно объявлений ({num_listings}) для диапазона: {current_min_price} - {current_max_price}. Увеличиваем диапазон.")
                current_max_price += INCREASE_STEP
                num_listings = get_num_listings_for_range(driver, base_url, current_min_price, current_max_price)

if num_listings >= MAX_LISTINGS:
                print(f"Подходящий диапазон найден: {current_min_price} - {current_max_price}, количество объявлений: {num_listings}")
                listings = scrape_all_pages(driver, base_url, current_min_price, current_max_price)
                all_listings.extend(listings)
                current_min_price = current_max_price
                step = INITIAL_STEP
            elif num_listings < MAX_LISTINGS and current_max_price >= end_price:
                print(f"Подходящий диапазон найден: {current_min_price} - {current_max_price}, количество объявлений: {num_listings}")
                listings = scrape_all_pages(driver, base_url, current_min_price, current_max_price)
                all_listings.extend(listings)
                current_min_price = current_max_price
                break
    except KeyboardInterrupt:
        print("Процесс был прерван пользователем.")
    except Exception as e:
        print(f"Ошибка при обработке диапазона: {e}")
    finally:
        driver.quit()
        save_listings(all_listings)

    return all_listings

def process_price_ranges(base_url, ranges, step):
    all_listings = []
    for start_price, end_price in ranges:
        print(f"Обработка диапазона цен от {start_price} до {end_price}")
        listings = filter_by_price(base_url, start_price, end_price, step)
        all_listings.extend(listings)
    save_listings(all_listings)

def save_listings(listings):
    with open('listings.json', 'w', encoding='utf-8') as f:
        json.dump(listings, f, ensure_ascii=False, indent=4)

if name == 'main':
    base_url = input('Введите базовый URL: ')
    MAX_LISTINGS = int(input('Введите максимальное количество объявлений: '))
    INCREASE_STEP = int(input('Введите шаг увеличения диапазона цен: '))
    INITIAL_STEP = int(input('Введите начальный шаг диапазона цен: '))
    
    ranges = [(0, 10_000_000_000)]
    step = INITIAL_STEP
    process_price_ranges(base_url, ranges, step)
