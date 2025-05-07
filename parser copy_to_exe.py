import cianparser
import pandas as pd
import json
import pandas
from datetime import datetime
import matplotlib.pyplot as plt

# Константы
current_date_str = datetime.now().strftime('%Y-%m-%d-%M-%H')

def all_flar_search():
    # Значения поиска по умолчанию
    Search_value_default={"Количество комнат": "all", "Только квартиры" : True, 
            "Аппартаменты" :False, "Минимальный год постройки" : "2024", "Первая страница поиска" :1,
            "Последняя страница поиска" : 20, "Минимальная цена" : 0, "Максимальная цена": 30000000
            }    
    # Словарь для перевода слов из файла ввода данных
    
    # Грузим файл, проверяем его значения, если не пусто то вставляем key+value, если значение none берём кей и валуе из дефалта
    nsk_parser = cianparser.CianParser(location="Новосибирск")
    data = nsk_parser.get_flats( deal_type="sale", 
                                rooms=Search_value_default["Количество комнат"], with_saving_csv=True,
                                additional_settings = {"only_flat": Search_value_default['Только квартиры'], 
                                                    "only_apartment":Search_value_default['Аппартаменты'],
                                                        "min_house_year": Search_value_default['Минимальный год постройки'],
                                                            "start_page":Search_value_default['Первая страница поиска'],
                                                            "end_page": Search_value_default['Последняя страница поиска'],
                                                            "object_type":"new", 
                                                                "min_price": Search_value_default['Минимальная цена'],
                                                                "max_price": Search_value_default['Максимальная цена'] } ,  with_extra_data=True)

     #преобразовываем в excel и сохраняем всю информацию
    df=pd.DataFrame(data)
    df.to_excel(f"./result/all_flat_result{current_date_str}.xlsx") 

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