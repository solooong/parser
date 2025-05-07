import os




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
            import parser  
            parser.new_dev()
        elif search_type == 2:
            import parser  # Предполагается, что есть модуль parser
            parser.all_flar_search()
        else:
            print("Ошибка: Неверный выбор типа поиска.")

    elif action == 2:
        import sorting  # Предполагается, что есть модуль sorting
        sorting.sorting()

    elif action == 3:
        print("Поиск маркетинговых активностей застройщиков.")
        import search
        search.main()
        # Здесь можно добавить соответствующую логику

    else:
        print("Ошибка: Неверный номер действия.")

except ValueError:
    print("Ошибка: Введите корректный номер.")