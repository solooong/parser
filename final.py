import os
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
import cianparser
import pandas as pd
import json
import pandas
from datetime import datetime
import matplotlib.pyplot as plt
import json
from fuzzywuzzy import fuzz
# Сбор данных улиц по карте https://www.openstreetmap.org/#map=3/69.62/-74.90
# Константы
current_date_str = datetime.now().strftime('%Y-%m-%d-%M-%H')
# Значения для районов
disct={"Октябрьский": 215, "Кировский": 213}
# Поиск новых ЖК

# === Переменная для остановки парсинга ===
stop_flag = False

# === Установка флага остановки ===
def set_stop_flag():
    global stop_flag
    stop_flag = True

# === Сброс флага ===
def reset_stop_flag():
    global stop_flag
    stop_flag = False

# === Парсинг новостроек ===
def new_dev(stop_event=None):
    try:
        print("Запуск парсинга новостроек...")
        nsk_parser = cianparser.CianParser(location="Новосибирск")
        data = []
        for i in range(1, 10):  # Имитация долгого парсинга
            if stop_event and stop_event.is_set():
                print("Парсинг новостроек остановлен.")
                return None
            print(f"Получение данных ЖК {i}...")
            chunk = nsk_parser.get_newobjects(with_saving_csv=False)
            data.extend(chunk)
            time.sleep(0.5)  # имитация задержки при парсинге
        df = pd.DataFrame(data)
        current_date_str = datetime.now().strftime('%Y-%m-%d-%M-%H')
        output_file = f"./result/new_object_{current_date_str}.xlsx"
        df.to_excel(output_file, index=False)
        print(f"Парсинг завершён. Результаты сохранены в {output_file}")
        return output_file
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        return None

# === Поиск квартир ===
def all_flar_search_gui(params, stop_event=None):
    try:
        print("Запуск поиска квартир...")
        nsk_parser = cianparser.CianParser(location="Новосибирск")
        data = []
        start_page = params.get("start_page", 1)
        end_page = params.get("end_page", 5)

        for page in range(start_page, end_page + 1):
            if stop_event and stop_event.is_set():
                print("Парсинг квартир остановлен.")
                return None
            print(f"Парсинг страницы {page}...")
            result = nsk_parser.get_flats(
                deal_type="sale",
                rooms=params.get("rooms", "all"),
                with_saving_csv=False,
                additional_settings={
                    "only_flat": params.get("only_flat", True),
                    "only_apartment": params.get("only_apartment", False),
                    "min_house_year": params.get("min_house_year", 2024),
                    "start_page": page,
                    "end_page": page,
                    "object_type": params.get("object_type", "secondary"),
                    "min_price": params.get("min_price", 0),
                    "max_price": params.get("max_price", 30000000),
                    "district": params.get("district", None),
                    "house_material_type": params.get("house_material_type", None),
                    "metro": params.get("metro", None),
                    "metro_station": params.get("metro_station", None),
                    "metro_foot_minute": params.get("metro_foot_minute", None),
                    "is_by_homeowner": params.get("is_by_homeowner", None),
                    "flat_share": params.get("flat_share", None),
                    "sort_by": params.get("sort_by", None)
                },
                with_extra_data=True
            )
            data.extend(result)
            time.sleep(0.5)

        df = pd.DataFrame(data)
        current_date_str = datetime.now().strftime('%Y-%m-%d-%M-%H')
        output_file = f"./result/all_flat_result_{current_date_str}.xlsx"
        df.to_excel(output_file, index=False)
        print(f"Парсинг завершён. Результаты сохранены в {output_file}")
        return output_file
    except Exception as e:
        print(f"Ошибка парсинга квартир: {e}")
        return None


def all_flat_search_gui(params):
    current_date_str = datetime.now().strftime('%Y-%m-%d-%M-%H')
    nsk_parser = cianparser.CianParser(location="Новосибирск")
    data = nsk_parser.get_flats(
        deal_type="sale",
        rooms=params.get("rooms"),
        with_saving_csv=True,
        additional_settings={
            "only_flat": params.get("only_flat"),
            "only_apartment": params.get("only_apartment"),
            "min_house_year": params.get("min_house_year"),
            "start_page": params.get("start_page"),
            "end_page": params.get("end_page"),
            "object_type": params.get("object_type"),
            "min_price": params.get("min_price"),
            "max_price": params.get("max_price"),
            "district": params.get("district"),
            "house_material_type": params.get("house_material_type"),
            "metro": params.get("metro"),
            "metro_station": params.get("metro_station"),
            "metro_foot_minute": params.get("metro_foot_minute"),
            "is_by_homeowner": params.get("is_by_homeowner"),
            "flat_share": params.get("flat_share"),
            "sort_by": params.get("sort_by"),
        },
        with_extra_data=True
    )
    df = pd.DataFrame(data)
    df.to_excel(f"./result/all_flat_result_{current_date_str}.xlsx")
    return f"./result/all_flat_result_{current_date_str}.xlsx"

def files():
    folder_path = './result'  # Путь к папке
    extension = '.xlsx'  # Расширение файлов для поиска

    # Проверка существования папки
    if not os.path.exists(folder_path):
        print(f"Ошибка: Папка {folder_path} не существует.")
        return None

    # Получаем список файлов с указанным расширением
    files = [f for f in os.listdir(folder_path) if f.endswith(extension)]

    # Если файлы не найдены
    if not files:
        print(f"Файлы с расширением {extension} не найдены.")
        return None

    # Вывод списка файлов
    print(f"Файлы с расширением {extension}:")
    for i, file in enumerate(files, start=1):
        print(f"{i}. {file}")

    # Запрос выбора файла
    try:
        choice = int(input("Выберите файл путём ввода номера: "))
        if 1 <= choice <= len(files):
            selected_file = files[choice - 1]
            print(f"Выбран файл: {selected_file}")
            return selected_file
        else:
            print("Ошибка: Неверный номер файла.")
            return None
    except ValueError:
        print("Ошибка: Введите корректный номер.")
        return None

def sorting(file_path=None, filter_streets=None):
    import pandas as pd
    import matplotlib.pyplot as plt
    from fuzzywuzzy import fuzz
    import os

    if file_path is None:
        name_file = files()
        file_path = f"./result/{name_file}"

    df = pd.read_excel(file_path)

    # Фильтрация по улицам
    if filter_streets:
        street_list = [s.strip().lower() for s in filter_streets.split(",") if s.strip()]
        street_col = None
        for col in df.columns:
            if col.lower() in ['street', 'улица']:
                street_col = col
                break
        if street_col:
            df = df[df[street_col].str.lower().isin(street_list)]
    #     df.groupby(['residential_complex', 'rooms_count'])
    #     .agg(mean_price=('price_metr', 'mean'))
    #     .sort_values(by=['mean_price'])
    # )
    
    # Ввод данных пользователем
    try:
        sorting_parametr=int(input("График сравнение стоимости расчитать по \n 1. Цена кв.м., \n 2. Цена квартиры \n 3. Общая площадь квартиры: "))
        if sorting_parametr==1:
            dev_sorting = (df.groupby(['residential_complex', 'rooms_count']).agg(mean_price=('price_metr', 'mean')).sort_values(by=['mean_price']))
        elif sorting_parametr==2:
            dev_sorting = (df.groupby(['residential_complex', 'rooms_count']).agg(mean_price=('price', 'mean')).sort_values(by=['mean_price']))
        elif sorting_parametr==3:
            dev_sorting = (df.groupby(['residential_complex', 'rooms_count']).agg(mean_price=('total_meters', 'mean')).sort_values(by=['mean_meters']))
        
        room = int(input('Введите количество комнат квартиры для сравнения: '))
        
        # Получение уникальных застройщиков из базы данных
        unique_developers = df['residential_complex'].dropna().astype(str).unique()
        
        while True:
            developers_input = input('Введите застройщиков для сравнения (через запятую): ').strip()
            developers = [dev.strip() for dev in developers_input.split(",") if dev.strip()]
            
            # Проверка схожести введенных значений с базой данных
            valid_developers = []
            invalid_developers = []
            for dev in developers:
                matches = [(fuzz.ratio(dev.lower(), unique_dev.lower()), unique_dev) for unique_dev in unique_developers]
                best_match = max(matches, key=lambda x: x[0])  # Находим наиболее похожее значение
                
                if best_match[0] >= 80:  # Порог схожести 90%
                    valid_developers.append(best_match[1])
                else:
                    invalid_developers.append(dev)
            
            # Вывод результатов проверки
            if invalid_developers:
                print(f"Следующие застройщики не найдены или не соответствуют базе данных: {', '.join(invalid_developers)}")
                print("Пожалуйста, повторите ввод.")
            else:
                break
        # Проверка количества застройщиков
        if len(valid_developers) < 2:
            print("Ошибка: Введите как минимум двух застройщиков.")
            exit()
        # Фильтрация данных по введенным застройщикам и комнатам
        filtered_data = dev_sorting[
            (dev_sorting.index.get_level_values('rooms_count') == room) &
            (dev_sorting.index.get_level_values('residential_complex').isin(valid_developers))
        ]   
        # Исключение застройщиков, не входящих в список
        excluded_data = dev_sorting[
            ~dev_sorting.index.get_level_values('residential_complex').isin(valid_developers)
        ]  
        # Вывод результатов
        print("\nРезультаты для выбранных застройщиков:")
        print(filtered_data)
    except ValueError:
        print("Ошибка: Введите корректные данные.")        

        # Построение графиков для фильтрованных данных
        # Выборка очередной группы
        chunk = filtered_data
        # Построение графика
        fig, ax = plt.subplots(figsize=(12, 8))
        chunk.unstack().plot(kind='barh', ax=ax)  # Горизонтальные столбцы для лучшей читаемости
        plt.title(f'Средняя цена квадратного метра (Группа {developers_input})', fontsize=16)
        plt.xlabel('Средняя цена за квадратный метр', fontsize=12)
        plt.ylabel('Застройщик и количество комнат', fontsize=12)
        plt.legend(title='Количество комнат')
        plt.tight_layout()  # Автоматическая настройка макета
        # Сохранение графика
        output_file = f'./result/output_plot_group{developers_input}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
    filtered_file = file_path.replace('.xlsx', '_filtered.xlsx')
    df.to_excel(filtered_file, index=False)
    return filtered_file



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

                # Скриншот
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_name = f"./result/{developer.replace(' ', '_')}_{timestamp}.png"
                try:
                    take_screenshot(url, screenshot_name)
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


def main():
    # Основная программа
    print('Доступные действия:')
    print('1. Парсинг объявлений')
    print('2. Обработка данных')
    print('3. Поиск маркетинговых активностей застройщиков')

    try:
        action = int(input('Введите номер действия: '))

        if action == 1:
            print("Доступные действия по поиску объектов недвижимости:")
            print("1. Поиск по новостройкам - вывод информации в файл по всем ЖК")
            print("2. Поиск квартир по параметрам - необходимо заполнить файл Excel в папке Data -> Input")

            search_type = int(input("Выберите тип поиска: "))
            if search_type == 1:
                new_dev()
            elif search_type == 2:
                all_flar_search()
            else:
                print("Ошибка: Неверный выбор типа поиска.")

        elif action == 2:
            sorting()

        elif action == 3:
            print("Поиск маркетинговых активностей застройщиков.")
            searchhh()
            # Здесь можно добавить соответствующую логику

        else:
            print("Ошибка: Неверный номер действия.")

    except ValueError:
        print("Ошибка: Введите корректный номер.")

if __name__ == "__main__":
    main()