from googlesearch import search
import pandas as pd
from datetime import datetime
import logging
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import os

# --- Настройка повторных попыток для requests ---
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

def normalize_url(url):
    parsed = urlparse(url)
    cleaned = parsed._replace(query='', fragment='')
    return urlunparse(cleaned).lower().rstrip('/')

def get_search_results(query, num_results=9):
    return [result for result in search(query, num_results=num_results)]

def find_keywords(url, keywords):
    try:
        response = requests.get(url, timeout=25)
        soup = BeautifulSoup(response.text, 'lxml')
        return [kw for kw in keywords if kw.lower() in soup.get_text().lower()]
    except Exception as e:
        print(f"Ошибка при обработке {url}: {e}")
        return []

def take_screenshot(url, filename):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1200, 900)
    try:
        driver.get(url)
        time.sleep(3)
        driver.save_screenshot(filename)
    except Exception as e:
        print(f"Ошибка при создании скриншота {url}: {e}")
    finally:
        driver.quit()

def searchhh(city=None, developers=None):
    """
    city: строка с названием города (например, "Новосибирск")
    developers: список ЖК/застройщиков для поиска (например, ["Ясный берег", "Академ Riverside"])
    """
    # Если запуск из консоли, запросить ввод
    if city is None:
        city = input('Введите город поиска: ')
    if developers is None or not developers:
        dev = input('Введите застройщика/ЖК: ')
        developers = [f"ЖК {dev} {city}"]

    # Ключевые слова для поиска маркетинговых активностей
    keywords = [
        'обменяй','новая','на новую','успей', 'ипотеку',' обмене',' в счёт','примем вашу',
        ' взнос',' зафиксируем','обмен',' скидка',' выгода',
        ' минус',' ценопад', 'день рожденье', 'семья','дети','ребенок', 'счастливый час','семейная'
    ]

    results = []
    current_date_str = datetime.now().strftime('%Y-%m-%d')
    os.makedirs('./result', exist_ok=True)
    excel_file = f"./result/Result_{current_date_str}.xlsx"
    processed_urls = {}
    print('Получены данные. Приступаем к поиску')
    for developer in developers:
        processed_urls[developer] = set()
        search_queries = [f"{developer} {keyword}" for keyword in keywords]
        print(f"\nПоиск для: {developer}")
        for query in search_queries:
            try:
                search_results = get_search_results(query)
            except Exception as e:
                print(f"Ошибка поиска для {query}: {e}")
                continue

            for raw_url in search_results[:5]:
                url = normalize_url(raw_url)
                if url in processed_urls[developer]:
                    continue
                processed_urls[developer].add(url)
                found_keywords = find_keywords(url, keywords)
                if not found_keywords:
                    continue

                print('Делаем скриншот найденного результата') 
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_name = f"./result/{developer.replace(' ', '_')}_{timestamp}.png"
                try:
                    take_screenshot(url, screenshot_name)
                    print(f'Найден сайт и сделан скриншот. Файл сохранён result/{developer}{city}_{timestamp}')
                except Exception as e:
                    print(f"Скриншот не создан для {url}: {e}")

                results.append({
                    "developer": developer,
                    "query": query,
                    "url": url,
                    "found_keywords": ', '.join(found_keywords),
                    "screenshot": screenshot_name
                })

    # Сохраняем результаты в Excel
    if results:
        df = pd.DataFrame(results)
        df.to_excel(excel_file, index=False)
        print(f"\nРезультаты сохранены в {excel_file}")
    else:
        print("По вашему запросу ничего не найдено.")

    return excel_file if results else None

