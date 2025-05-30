import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import pandas as pd
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from fuzzywuzzy import fuzz
import time
import sys

# Категории Kuper.ru
KUPER_CATEGORIES = {
    "Молочные продукты": "https://kuper.ru/lentagp/c/moloko-sir-yajtsa-rastitelnie-produkti-c44b0ed/vse-tovari-kategorii-c96b427",
    "Хлеб и выпечка": "https://kuper.ru/lentagp/c/khleb-khlebtsi-vipechka/vse-tovari-kategorii-8385705",
    "Бытовая химия": "https://kuper.ru/lentagp/c/bitovaya-himiya-uborka-/vse-tovari-kategorii-d277e9a",
    "Консервы": "https://kuper.ru/lentagp/c/konservi-solenya-copy/vse-tovari-kategorii-14ddd57"
}

class ParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Парсер цен на продукты")

        # Переменные
        self.stop_flag = False
        self.save_interval = 5
        self.monitoring_mode = tk.IntVar(value=0)  # 0 - не выбрано, 1 - группа, 2 - поиск по названию
        self.kuper_var = tk.BooleanVar()
        self.price_limit_var = tk.BooleanVar()
        self.price_limit_entry = None
        self.save_var = tk.BooleanVar(value=True)
        self.name_entry = None
        self.name_label = None
        self.group_vars = {}
        self.driver = None

        # GUI
        self.create_widgets()

    def create_widgets(self):
        # Шаг 1: Выбор источников
        frame_sources = ttk.LabelFrame(self.root, text="Шаг 1: Выберите источник")
        frame_sources.pack(pady=10, fill="x", padx=10)

        ttk.Checkbutton(frame_sources, text="Купер.Лента", variable=self.kuper_var).pack(side="left", padx=5)

        # Шаг 2: Варианты мониторинга
        frame_monitoring = ttk.LabelFrame(self.root, text="Шаг 2: Варианты мониторинга")
        frame_monitoring.pack(pady=10, fill="x", padx=10)

        ttk.Radiobutton(frame_monitoring, text="Мониторинг группы товаров", variable=self.monitoring_mode, value=1,
                        command=self.show_group_selection).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(frame_monitoring, text="Мониторинг по наименованию", variable=self.monitoring_mode, value=2,
                        command=self.show_name_input).grid(row=1, column=0, sticky="w")

        # Группы
        self.group_frame = ttk.Frame(frame_monitoring)
        row = 2
        for group in KUPER_CATEGORIES.keys():
            var = tk.BooleanVar()
            self.group_vars[group] = var
            ttk.Checkbutton(self.group_frame, text=group, variable=var).grid(row=row, column=0, sticky="w")
            row += 1

        # Поле ввода имени
        self.name_entry = ttk.Entry(frame_monitoring, width=40)
        self.name_label = ttk.Label(frame_monitoring, text="Введите наименование товара:")

        # Опции
        options_frame = ttk.Frame(self.root)
        options_frame.pack(pady=10)

        ttk.Checkbutton(options_frame, text="Сохранять каждые 5 страниц", variable=self.save_var).pack(side="left", padx=5)

        self.price_limit_entry = ttk.Entry(options_frame, width=10)
        ttk.Checkbutton(options_frame, text="Ограничить цену до", variable=self.price_limit_var,
                        command=lambda: self.price_limit_entry.config(
                            state="normal" if self.price_limit_var.get() else "disabled")).pack(side="left", padx=5)
        self.price_limit_entry.pack(side="left")
        self.price_limit_entry.config(state="disabled")

        # Кнопки
        start_button = ttk.Button(self.root, text="Начать парсинг", command=self.start_in_thread)
        start_button.pack(pady=10)

        stop_button = ttk.Button(self.root, text="СТОП", command=self.stop_parsing)
        stop_button.pack(pady=5)

        # Лог
        self.log_text = scrolledtext.ScrolledText(self.root, height=10)
        self.log_text.pack(padx=10, pady=5, fill="both", expand=True)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def show_group_selection(self):
        self.name_entry.grid_forget()
        self.name_label.grid_forget()
        self.group_frame.grid(row=2, column=0, sticky="w")

    def show_name_input(self):
        self.group_frame.grid_forget()
        self.name_label.grid(row=2, column=0, sticky="w")
        self.name_entry.grid(row=3, column=0, sticky="w")

    def start_in_thread(self):
        thread = Thread(target=self.start_parsing)
        thread.start()

    def start_parsing(self):
        self.stop_flag = False
        self.log("Начало парсинга...")

        mode = self.monitoring_mode.get()
        self.log(f"[DEBUG] monitoring_mode = {mode}")

        if mode == 0:
            self.log("Ошибка: Выберите способ мониторинга на шаге 2.")
            return

        sources = []
        if self.kuper_var.get():
            sources.append("Купер")
        if not sources:
            self.log("Выберите хотя бы один источник.")
            return

        # Настройка браузера
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Headless mode
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    delete navigator.__proto__.webdriver;
                    window.chrome = {runtime: {}};
                '''
            })

            if mode == 1:
                selected = [g for g, v in self.group_vars.items() if v.get()]
                self.log(f"[DEBUG] Выбранные группы: {selected}")
                if not selected:
                    self.log("Ошибка: не выбрана ни одна группа.")
                    self.driver.quit()
                    return
                if len(selected) > 2:
                    self.log("Ошибка: нельзя выбрать больше 2 групп.")
                    self.driver.quit()
                    return
                self.parse_by_group(sources, selected)
            elif mode == 2:
                query = self.name_entry.get().strip()
                if not query:
                    self.log("Введите название товара.")
                    self.driver.quit()
                    return
                self.parse_by_name(sources, query)

        except Exception as e:
            self.log(f"[Ошибка при запуске браузера] {e}")
        finally:
            self.log("Парсинг завершён.")
            if self.driver:
                self.driver.quit()

    def load_page(self, url, selector):
        """Загружает страницу и ожидает нужные элементы"""
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return True
        except:
            self.log(f"[Ошибка] Не найдены товары на странице: {url}")
            return False

    def parse_by_group(self, sources, groups):
        data = []
        for source in sources:
            if source == "Купер":
                for group in groups:
                    base_url = KUPER_CATEGORIES[group]
                    page_num = 1
                    while not self.stop_flag:
                        url = base_url if page_num == 1 else f"{base_url}?page={page_num}"
                        self.log(f"[Купер] Группа '{group}', страница {page_num}: {url}")

                        # Загружаем страницу
                        if not self.load_page(url, "div.ProductCard_root__zO_B9"):
                            break

                        products = self.driver.find_elements(By.CSS_SELECTOR, "div.ProductCard_root__zO_B9")
                        if not products:
                            self.log("На странице нет товаров.")
                            break

                        for product in products:
                            try:
                                name_elem = product.find_element(By.CSS_SELECTOR, "h3.ProductCard_title__iB_Dr")
                                name = name_elem.text.strip()

                                try:
                                    volume_elem = product.find_element(By.CSS_SELECTOR, "div.ProductCard_volume__RHLb0 span")
                                    volume = volume_elem.text.strip()
                                    name += f" ({volume})"
                                except:
                                    volume = None

                                try:
                                    price_old_elem = product.find_element(By.CSS_SELECTOR, "div.ProductCardPrice_originalPrice__TAcDj div.Price_price__X_7uT")
                                    price_old = float(price_old_elem.text.replace('₽', '').replace(' ', '').replace(',', '.'))
                                except:
                                    price_old = None

                                try:
                                    price_new_elem = product.find_element(By.CSS_SELECTOR, "div.ProductCardPrice_price__zSwp0 div.Price_price__X_7uT")
                                    price_new = float(price_new_elem.text.replace('₽', '').replace(' ', '').replace(',', '.'))
                                except:
                                    price_new = None

                                final_price = price_new if price_new is not None else price_old
                                if self.price_limit_var.get() and final_price:
                                    limit = float(self.price_limit_entry.get())
                                    if final_price > limit:
                                        continue

                                data.append({
                                    "Источник": source,
                                    "Наименование товара": name,
                                    "Цена до скидки": price_old,
                                    "Цена после скидки": price_new,
                                    "Дата сбора данных": pd.Timestamp.now()
                                })

                            except Exception as e:
                                self.log(f"[Ошибка товара] {str(e)}")
                                continue

                        # Пауза между запросами
                        time.sleep(2)

                        # Проверка на последнюю страницу
                        try:
                            next_btn = self.driver.find_element(By.CSS_SELECTOR, "a.Pagination_arrow__k3A9H[aria-label='Следующая страница']")
                            if "disabled" in next_btn.get_attribute("class"):
                                break
                            page_num += 1
                        except:
                            break

                        if self.save_var.get() and page_num % self.save_interval == 0:
                            self.save_to_excel(data, f"output_{source}_partial.xlsx")

                    # Сохраняем данные по группе
                    if data:
                        self.save_to_excel(data, f"output_{source}_group_{group}.xlsx")

    def parse_by_name(self, sources, query):
        data = []
        for source in sources:
            if source == "Купер":
                for group, base_url in KUPER_CATEGORIES.items():
                    page_num = 1
                    while not self.stop_flag:
                        url = base_url if page_num == 1 else f"{base_url}?page={page_num}"
                        self.log(f"[Купер] Поиск '{query}' в '{group}', страница {page_num}: {url}")

                        # Загружаем страницу
                        if not self.load_page(url, "div.ProductCard_root__zO_B9"):
                            break

                        products = self.driver.find_elements(By.CSS_SELECTOR, "div.ProductCard_root__zO_B9")
                        if not products:
                            break

                        for product in products:
                            try:
                                name_elem = product.find_element(By.CSS_SELECTOR, "h3.ProductCard_title__iB_Dr")
                                name = name_elem.text.strip()

                                ratio = fuzz.token_sort_ratio(query.lower(), name.lower())
                                if ratio < 85:
                                    continue

                                try:
                                    volume_elem = product.find_element(By.CSS_SELECTOR, "div.ProductCard_volume__RHLb0 span")
                                    volume = volume_elem.text.strip()
                                    name += f" ({volume})"
                                except:
                                    volume = None

                                try:
                                    price_old_elem = product.find_element(By.CSS_SELECTOR, "div.ProductCardPrice_originalPrice__TAcDj div.Price_price__X_7uT")
                                    price_old = float(price_old_elem.text.replace('₽', '').replace(' ', '').replace(',', '.'))
                                except:
                                    price_old = None

                                try:
                                    price_new_elem = product.find_element(By.CSS_SELECTOR, "div.ProductCardPrice_price__zSwp0 div.Price_price__X_7uT")
                                    price_new = float(price_new_elem.text.replace('₽', '').replace(' ', '').replace(',', '.'))
                                except:
                                    price_new = None

                                final_price = price_new if price_new is not None else price_old
                                if self.price_limit_var.get() and final_price:
                                    limit = float(self.price_limit_entry.get())
                                    if final_price > limit:
                                        continue

                                data.append({
                                    "Источник": source,
                                    "Наименование товара": name,
                                    "Цена до скидки": price_old,
                                    "Цена после скидки": price_new,
                                    "Дата сбора данных": pd.Timestamp.now()
                                })

                            except Exception as e:
                                self.log(f"[Ошибка товара] {str(e)}")
                                continue

                        # Пауза между запросами
                        time.sleep(2)

                        # Проверка на последнюю страницу
                        try:
                            next_btn = self.driver.find_element(By.CSS_SELECTOR, "a.Pagination_arrow__k3A9H[aria-label='Следующая страница']")
                            if "disabled" in next_btn.get_attribute("class"):
                                break
                            page_num += 1
                        except:
                            break

                    if data:
                        self.save_to_excel(data, f"output_search_{group}.xlsx")

    def save_to_excel(self, data, filename):
        df = pd.DataFrame(data)
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=filename)
        if path:
            df.to_excel(path, index=False)
            self.log(f"Сохранено в {path}")

    def stop_parsing(self):
        self.stop_flag = True
        self.log("Парсинг остановлен пользователем.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ParserApp(root)
    root.mainloop()
