import cianparser
import pandas as pd
import json
import pandas
from datetime import datetime
import matplotlib.pyplot as plt
# Сбор данных улиц по карте https://www.openstreetmap.org/#map=3/69.62/-74.90
# Константы
current_date_str = datetime.now().strftime('%Y-%m-%d-%M-%H')
# Значения для районов
disct={"Октябрьский": 215, "Кировский": 213}
# Поиск новых ЖК
def new_dev ():
    nsk_parser = cianparser.CianParser(location="Новосибирск")
    data = nsk_parser.get_newobjects(with_saving_csv=True)
    #преобразовываем в excel и сохраняем всю информацию
    # current_date_str = datetime.now().strftime('%Y-%m-%d-%H-%M')
    name_of_file=f"new_object_{current_date_str}"
    df=pd.DataFrame(data)
    df.to_excel(f"./result/{name_of_file}.xlsx") 

def mysearch():
    nsk_parser = NSKParser()
    url_of_user = "https://example.com/path?foo=bar"
    data = nsk_parser.get_url(url=url_of_user, with_extra_data=True)
    print(nsk_parser.final_url)  # Здесь будет финальный URL

def all_flat_search_gui(params):
    print('Приступаю к парсингу по заданным параметрам')

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

# Парсинг квартир
def all_flar_search():
    # Значения поиска по умолчанию
    Search_value_default={"Количество комнат": [1,2,3,4,"all"], "Только квартиры" : True, 
            "Аппартаменты" :False, "Минимальный год постройки" : "2024", "Первая страница поиска" :1,
            "Последняя страница поиска" : 20, "Минимальная цена" : 0, "Максимальная цена": 30000000,
            "Тип жилья":"secondary " , 'Район' : ''}    
    # Словарь для перевода слов из файла ввода данных
    dictionary = {
    "secondary ": ["Вторичка", 'вторичка']
    ,'new': ['Новостройка ', 'Новые', 'новостройка'],
    "all": ['все', 'Все'], 
    True: ['да', 'Да'], 
    False: ['нет', 'Нет'],
    215 : ['Октябрьский', 'октябрьский'],
    213 : ['кировский', 'Кировский'],
    209 : ['Дзержинский', 'дзержинский'],
    210 : ['железнодорожный', 'Железнодорожный'],
    211 : ['Заельцовский', 'заельцовский' ],
    214 : ['ленинский', 'Ленинский']}

# --- Чтение из Excel (раскомментируйте, если нужен ввод из файла) ---
# try:
#     input_df = pd.read_excel('./date/Input.xlsx')
#     input_df.dropna(inplace=True)
#     for option, value in zip(input_df['Option'], input_df['Value']):
#         mapped = None
#         for key, synonyms in dictionary.items():
#             if str(value).strip().lower() in [s.lower() for s in synonyms]:
#                 mapped = key
#                 break
#         Search_value_default[option] = mapped if mapped is not None else value
# except FileNotFoundError:
#     print("Файл с вводом не найден, пропускаем.")

# --- Ввод с клавиатуры ---
    for key in Search_value_default:
        while True:
            current_value = Search_value_default[key]
            prompt = f"Введите значение для параметра '{key}' (текущее: {current_value}): "
            user_input = input(prompt).strip()

            # Если пустой ввод - оставляем текущее значение
            if user_input == "":
                break

            # Обработка специальных случаев
            if key == "Количество комнат":
                if user_input.lower() in ["1", "2", "3", "4", "all"]:
                    Search_value_default[key] = user_input if user_input == "all" else int(user_input)
                    break
                else:
                    print("Ошибка: допустимые значения - 1, 2, 3, 4 или all")
            elif key in ["Только квартиры", "Аппартаменты"]:
                if user_input.lower() in ["true", "false"]:
                    Search_value_default[key] = user_input.lower() == "true"
                    break
                else:
                    print("Ошибка: введите 'true' или 'false'")
            elif key in ["Первая страница поиска", "Последняя страница поиска"]:
                if user_input.lower() and int(user_input) in range(1, 101):
                    Search_value_default[key] = int(user_input)
                    break
                else:
                    print("Ошибка: введите 'true' или 'false'")

            else:
                # Для остальных параметров - просто сохраняем введённое значение
                Search_value_default[key] = user_input
                break

    print("\nОбновленные значения:")
    for key, value in Search_value_default.items():
        print(f"{key}: {value}")
    # Грузим файл, проверяем его значения, если не пусто то вставляем key+value, если значение none берём кей и валуе из дефалта
    nsk_parser = cianparser.CianParser(location="Новосибирск")
    data = nsk_parser.get_flats( deal_type="sale", 
                                rooms=Search_value_default["Количество комнат"], with_saving_csv=True, 
                                additional_settings = {"only_flat": Search_value_default['Только квартиры'], 
                                                    "only_apartment":Search_value_default['Аппартаменты'],
                                                        "min_house_year": Search_value_default['Минимальный год постройки'],
                                                            "start_page":Search_value_default['Первая страница поиска'],
                                                            "end_page": Search_value_default['Последняя страница поиска'],
                                                            "object_type":"secondary", "residential_complex": "VIRA",
                                                                "min_price": Search_value_default['Минимальная цена'],
                                                                "max_price": Search_value_default['Максимальная цена'] , 
                                                                "district" : Search_value_default['Район']} ,  with_extra_data=True)

    print('Преобразовываем в excel и сохраняем всю информацию')
    df=pd.DataFrame(data)
    df.to_excel(f"./result/all_flat_result{current_date_str}.xlsx") 
    print(f'Данные сохранены в файл /result/all_flat_result{current_date_str}.xlsx')

    #расчёт цены квадратного метра и поиск уникальных значений для каждого застройщика
    df['price_metr']=(df['price'].astype(int) / df['total_meters'].astype(int)) 
    result = df.groupby(['residential_complex', 'rooms_count','price_metr', 'price','total_meters']).size().reset_index(name='count')
    sort_df=df.groupby(['residential_complex', 'rooms_count']).agg(
        min_price_of_metr=('price_metr','min'),
        max_price_of_metr =('price_metr','max'),
        mean_price_of_metr=('price_metr','mean'), 
        size=('rooms_count','size')).reset_index()
    #уникальные значения застройщиков
    Unique_Realty=pd.DataFrame(df['residential_complex'].unique())
    # dev_sorting=df.groupby(['residential_complex', 'rooms_count']).agg(mean_price=('price_metr', 'mean'))
    # chunk_size = 25
    # for i in range(0, len(dev_sorting), chunk_size):
    #     # Выборка очередной группы
    #     chunk = dev_sorting.iloc[i:i + chunk_size]
    #     # Построение графика
    #     fig, ax = plt.subplots(figsize=(12, 8))
    #     chunk.unstack().plot(kind='barh', ax=ax)  # Горизонтальные столбцы для лучшей читаемости
    #     plt.title(f'Средняя цена квадратного метра (Группа {i // chunk_size + 1})', fontsize=16)
    #     plt.xlabel('Средняя цена за квадратный метр', fontsize=12)
    #     plt.ylabel('Застройщик и количество комнат', fontsize=12)
    #     plt.legend(title='Количество комнат')
    #     plt.tight_layout()  # Автоматическая настройка макета
    #     # Сохранение графика
    #     output_file = (f'output_plot_group{current_date_str}_{i // chunk_size + 1}.png')
    #     plt.savefig(output_file, dpi=300, bbox_inches='tight')
    # Запись в один файл
    with pd.ExcelWriter(f"./result/{current_date_str}_final.xlsx", engine='xlsxwriter', mode='w') as writer:
        df.to_excel(writer, sheet_name='Total')
        result.to_excel(writer, sheet_name='Sheet1')
        Unique_Realty.to_excel(writer, sheet_name='Sheet2')
        sort_df.to_excel(writer, sheet_name='Sheet3')

all_flar_search()