import  pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from fuzzywuzzy import fuzz

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
    
        # Закрытие графика
        
main()