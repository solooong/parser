from googlesearch import search
import pandas as pd
from datetime import datetime
import logging
import pandas as pd
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

try:
    response = session.get("https://example.com", timeout=10)
    print(response.text)
except requests.exceptions.Timeout:
    print("The request timed out after multiple attempts")
    
def normalize_url(url):
    parsed = urlparse(url)
    # Убираем параметры и якоря
    cleaned = parsed._replace(query='', fragment='')
    return urlunparse(cleaned).lower().rstrip('/')

def get_search_results(query, num_results=9):
    return [result for result in search(query, num_results=num_results)]


def find_keywords(url, keywords):
    try:
        response = requests.get(url, timeout=25)
        soup = BeautifulSoup(response.text, 'lxml')
        return [kw for kw in keywords if kw.lower() in soup.get_text().lower()]
    except:
        return []

def take_screenshot(url, filename):
    options = Options()
    
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.save_screenshot(filename)
    driver.quit()

def main():
    # Инициализация данных - далее чтение из файлов данных
    developers = []
    keywords=[]
    city=input('Введите город поиска ')
    developers = [f" ЖК {input('Введите застройщика ')}  {city} "]
    # with open("./date/keyword.txt", "r", encoding="utf-8") as file:
    #     keywords= [line2.strip() for line2 in file]
    # print(developers)
  
    # Инициализация данных - далее предустановленные данные по застройщикам
    # developers = ["ясный берег новосибирск"]  # Ваш список застройщиков
    keywords = ['обменяй','новая','на новую','успей', 'ипотеку',' обмене',' в счёт','примем вашу',
                ' взнос',' зафиксируем','обмен',' скидка',' выгода',
                ' минус',' ценопад', 'день рожденье', 'семья','дети','ребенок', 'счастливый час','семейная']    # Словарь ключевых слов
    # base_sites = ['https://sibakademstroy.brusnika.ru/']  # База сайтов ЖК не используется
    
    results=[]
    current_date_str = datetime.now().strftime('%Y-%m-%d')
    name_of_file=f"Result_{current_date_str}"
    processed_urls = {}
    for developer in developers:
        processed_urls[developer] = set()
        search_queries = [f"{developer} {keyword} " for keyword in keywords ]
        print(search_queries)
        
        for query in search_queries:
            try:
                search_results = get_search_results(query)
            except Exception as e:
                print(f"Ошибка поиска для {query}: {e}")
                continue

            for raw_url in search_results[:5]:
                url = normalize_url(raw_url)

                # Проверка уникальности
                if url in processed_urls[developer]:
                    print(f"URL уже проверен: {url}")
                    continue

                   # Добавление в обработанные
                processed_urls[developer].add(url)

                # Основная логика обработки
                found_keywords = find_keywords(url, keywords)
                if not found_keywords:
                    continue

                # Создание скриншота и запись результатов
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                screenshot_name = f"./result/screenshot_{timestamp}.png"
                take_screenshot(url, screenshot_name)
                
                results.append({
                    "Застройщик": developer,
                    "Ссылка": url,
                    "Ключевое слово": ", ".join(found_keywords),
                    "Скриншот": screenshot_name
                })
               # сохранение каждых 5ти результатов в файл темп
            df_temp=pd.DataFrame(results)
            df_temp.to_excel(f"{name_of_file}_temp.xlsx", index=False)
            time.sleep(1)
    
    # Экспорт в Excel
    df = pd.DataFrame(results)
    df.to_excel(f"./result/marketing_actions_{name_of_file}.xlsx", index=False)

logging.basicConfig(filename='./result/parser.log', level=logging.ERROR)
if __name__ == "__main__":
    main()

