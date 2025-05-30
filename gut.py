import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sys
import os

# Убедиться, что final.py находится в той же папке
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from final import new_dev, all_flar_search_gui, sorting, searchhh
except ImportError as e:
    messagebox.showerror("Ошибка импорта", f"Не удалось загрузить final.py:\n{e}")
    raise

class RedirectText:
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.config(state=tk.NORMAL)
        self.text_space.insert(tk.END, string)
        self.text_space.see(tk.END)
        self.text_space.config(state=tk.DISABLED)

    def flush(self):
        pass

class ParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Парсер недвижимости")
        self.root.geometry("800x600")

        # Лог-вывод
        self.log_text = tk.Text(root, wrap='word', state='disabled', height=20)
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        sys.stdout = RedirectText(self.log_text)

        # Контейнер для кнопок
        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(pady=10)

        # Кнопки действий
        self.btn_new_dev = tk.Button(self.btn_frame, text="1. Парсинг новостроек", width=25, command=self.run_new_dev)
        self.btn_new_dev.pack(side=tk.LEFT, padx=5)

        self.btn_flat_search = tk.Button(self.btn_frame, text="2. Поиск квартир", width=25, command=self.open_flat_search_form)
        self.btn_flat_search.pack(side=tk.LEFT, padx=5)

        self.btn_sorting = tk.Button(self.btn_frame, text="3. Анализ данных", width=25, command=self.open_sorting_form)
        self.btn_sorting.pack(side=tk.LEFT, padx=5)

        self.btn_marketing = tk.Button(self.btn_frame, text="4. Маркетинг", width=25, command=self.open_marketing_form)
        self.btn_marketing.pack(side=tk.LEFT, padx=5)

        # Кнопка СТОП
        self.stop_button = tk.Button(self.btn_frame, text="СТОП", width=15, command=self.stop_task, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Статус выполнения
        self.status_label = tk.Label(root, text="Ожидание запуска", fg="green")
        self.status_label.pack(pady=10)

        self.stop_event = None

    def run_in_thread(self, func, *args):
        self.stop_event = threading.Event()
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Выполняется...")

        def wrapper():
            try:
                func(*args)
            finally:
                self.stop_button.config(state=tk.DISABLED)
                self.status_label.config(text="Готово или остановлено")

        thread = threading.Thread(target=wrapper)
        thread.start()

    def stop_task(self):
        if self.stop_event:
            self.stop_event.set()
            print("Пользователь нажал 'СТОП'. Завершение операции...")

    def run_new_dev(self):
        print("Запущен парсинг новостроек...")
        self.run_in_thread(new_dev, self.stop_event)

    def open_flat_search_form(self):
        form_window = tk.Toplevel(self.root)
        form_window.title("Параметры поиска квартир")
        form_window.geometry("400x500")

        # Словарь районов
        disct = {
            "Октябрьский": 215,
            "Кировский": 213,
            "Дзержинский": 209,
            "Железнодорожный": 210,
            "Заельцовский": 211,
            "Ленинский": 214
        }

        # Поля ввода
        tk.Label(form_window, text="Количество комнат").pack()
        rooms_entry = ttk.Combobox(form_window, values=["all", "1", "2", "3", "4"])
        rooms_entry.set("all")
        rooms_entry.pack(pady=5)

        tk.Label(form_window, text="Только квартиры (True/False)").pack()
        only_flat_entry = ttk.Combobox(form_window, values=["True", "False"])
        only_flat_entry.set("True")
        only_flat_entry.pack(pady=5)

        tk.Label(form_window, text="Апартаменты (True/False)").pack()
        apartments_entry = ttk.Combobox(form_window, values=["True", "False"])
        apartments_entry.set("False")
        apartments_entry.pack(pady=5)

        tk.Label(form_window, text="Минимальный год постройки").pack()
        year_entry = tk.Entry(form_window)
        year_entry.insert(0, "2024")
        year_entry.pack(pady=5)

        tk.Label(form_window, text="Первая страница поиска").pack()
        start_page_entry = tk.Entry(form_window)
        start_page_entry.insert(0, "1")
        start_page_entry.pack(pady=5)

        tk.Label(form_window, text="Последняя страница поиска").pack()
        end_page_entry = tk.Entry(form_window)
        end_page_entry.insert(0, "20")
        end_page_entry.pack(pady=5)

        tk.Label(form_window, text="Минимальная цена").pack()
        min_price_entry = tk.Entry(form_window)
        min_price_entry.insert(0, "0")
        min_price_entry.pack(pady=5)

        tk.Label(form_window, text="Максимальная цена").pack()
        max_price_entry = tk.Entry(form_window)
        max_price_entry.insert(0, "30000000")
        max_price_entry.pack(pady=5)

        tk.Label(form_window, text="Район (выберите из списка)").pack()
        district_combo = ttk.Combobox(form_window, values=list(disct.keys()))
        district_combo.set("Октябрьский")
        district_combo.pack(pady=5)

        def submit():
            try:
                district_name = district_combo.get()
                district_id = disct.get(district_name, None)

                params = {
                    "rooms": rooms_entry.get(),
                    "only_flat": eval(only_flat_entry.get()),
                    "only_apartment": eval(apartments_entry.get()),
                    "min_house_year": int(year_entry.get()),
                    "start_page": int(start_page_entry.get()),
                    "end_page": int(end_page_entry.get()),
                    "min_price": int(min_price_entry.get()),
                    "max_price": int(max_price_entry.get()),
                    "district": district_id,
                    "object_type": "secondary",
                    "house_material_type": None,
                    "metro": None,
                    "metro_station": None,
                    "metro_foot_minute": None,
                    "is_by_homeowner": None,
                    "flat_share": None,
                    "sort_by": None
                }

                print(f"Запуск поиска квартир с параметрами: {params}")
                self.run_in_thread(all_flar_search_gui, params)
                form_window.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка ввода", f"Неверные данные:\n{e}")

        tk.Button(form_window, text="Запустить поиск", command=submit).pack(pady=10)

    def open_sorting_form(self):
        form_window = tk.Toplevel(self.root)
        form_window.title("Параметры анализа данных")
        form_window.geometry("400x300")

        tk.Label(form_window, text="Выберите файл Excel из ./result").pack()
        file_var = tk.StringVar()
        file_combo = ttk.Combobox(form_window, textvariable=file_var)
        try:
            file_combo['values'] = [f for f in os.listdir("./result") if f.endswith(".xlsx")]
        except FileNotFoundError:
            file_combo['values'] = []
        file_combo.pack(pady=5)

        tk.Label(form_window, text="Застройщики (через запятую)").pack()
        dev_entry = tk.Entry(form_window)
        dev_entry.pack(pady=5)

        tk.Label(form_window, text="Количество комнат для сравнения").pack()
        room_entry = tk.Entry(form_window)
        room_entry.insert(0, "2")
        room_entry.pack(pady=5)

        def submit():
            selected_file = file_var.get()
            devs = dev_entry.get()
            room = room_entry.get()
            if not selected_file:
                messagebox.showwarning("Файл не выбран", "Выберите файл Excel.")
                return
            if not devs:
                messagebox.showwarning("Нет застройщиков", "Введите хотя бы одного застройщика.")
                return

            print(f"Запуск анализа данных из файла: {selected_file}, застройщики: {devs}")
            self.run_in_thread(sorting, file_path=f"./result/{selected_file}", filter_streets=devs)
            form_window.destroy()

        tk.Button(form_window, text="Запустить анализ", command=submit).pack(pady=10)

    def open_marketing_form(self):
        form_window = tk.Toplevel(self.root)
        form_window.title("Поиск маркетинговых акций")
        form_window.geometry("400x300")

        tk.Label(form_window, text="Город поиска (например, Новосибирск)").pack()
        city_entry = tk.Entry(form_window)
        city_entry.insert(0, "Новосибирск")
        city_entry.pack(pady=5)

        tk.Label(form_window, text="Список застройщиков / ЖК (через запятую)").pack()
        devs_entry = tk.Entry(form_window)
        devs_entry.insert(0, "Ясный берег, Академ Riverside")
        devs_entry.pack(pady=5)

        def submit():
            city = city_entry.get().strip()
            devs = [d.strip() for d in devs_entry.get().split(",") if d.strip()]
            if not devs:
                devs = None

            print(f"Запуск поиска маркетинговых акций для города: {city}, застройщиков: {devs}")
            self.run_in_thread(lambda:  searchhh(city=city, developers=devs))
            form_window.destroy()

        tk.Button(form_window, text="Запустить поиск", command=submit).pack(pady=10)

    def run_sorting(self):
        self.status_label.config(text="Выполняется: Анализ данных...")
        self.run_in_thread(sorting)
        self.status_label.config(text="Готово: Анализ завершён.")

    def run_marketing(self):
        city = "Новосибирск"
        developers = ["Ясный берег", "Академ Riverside"]
        self.status_label.config(text=f"Выполняется: Поиск активностей для {city}...")
        self.run_in_thread(lambda:  searchhh(city=city, developers=developers))
        self.status_label.config(text="Готово: Результаты в Excel файле.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ParserGUI(root)
    root.mainloop()