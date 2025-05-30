import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import time
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
# === Константы по умолчанию ===
LOGIN = "laguta@nian.tv"
PASSWORD = "614084"


# === Функции сохранения/загрузки истории ссылок ===
def save_history(url):
    with open("history.txt", "a", encoding="utf-8") as f:
        f.write(url + "\n")


def load_history():
    if not os.path.exists("history.txt"):
        return []
    with open("history.txt", "r", encoding="utf-8") as f:
        return list(set(f.read().splitlines()))


# === Обработка URL: добавление &apartment и инкремент page ===
def increment_page_number(url):
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)

    # Убедимся, что URL содержит "apartment"
    if 'apartment' not in parsed.path and 'apartment' not in parsed.query:
        if parsed.query:
            new_query = parsed.query + "&apartment"
        else:
            new_query = "apartment"
        parsed = parsed._replace(query=new_query)
        url = urlunparse(parsed)

    # Обработка номера страницы
    if 'page' in query_params:
        current_page = int(query_params['page'][0])
        query_params['page'] = [str(current_page + 1)]
    else:
        query_params['page'] = ['2']

    # Собираем новый URL
    new_query = urlencode(query_params, doseq=True)
    parsed = parsed._replace(query=new_query)
    return urlunparse(parsed)


# === Парсинг данных с текущей страницы ===
def parse_data(html):
    soup = BeautifulSoup(html, "lxml")
    table_body = soup.select_one(".apartment-grid__table-tbody")
    if not table_body:
        print("❌ Таблица объявлений не найдена")
        return pd.DataFrame()  # Возвращаем пустой DataFrame

    headers = []
    for th in soup.select(".apartment-grid__table-th"):
        label_span = th.select_one(".apartment-grid-sort-button__label")
        if label_span:
            headers.append(label_span.text.strip())
    headers.append("Ссылка")

    data = []
    rows = table_body.select("tr.apartment-grid__table-tr")
    for row in rows:
        cols = row.select("td.apartment-grid__table-td:not(.apartment-grid__table-td-image)")
        cols_text = [col.get_text(strip=True) for col in cols]
        if len(cols_text) > 0:
            cols_text.pop(0)  # удалить первый столбец при необходимости
        link_container = row.select_one("img[src]")
        full_link = link_container["src"] if link_container else ""
        cols_text.append(full_link)
        data.append(cols_text)

    return pd.DataFrame(data, columns=headers)


# === Сохранение в Excel с поддержкой изображений ===
def save_to_excel_with_images(df, filename="flats.xlsx"):
    try:
        df = df.drop_duplicates(subset=('ЖК, оч. и корп.', '№'), keep="last")
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"✅ Данные сохранены в файл: {filename}")
    except Exception as e:
        print(f"❌ Ошибка при сохранении Excel: {e}")
        if os.path.exists(filename):
            os.remove(filename)
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"✅ Файл принудительно пересохранён: {filename}")


# === Объединение новых данных со старыми ===
def merge_new_data(new_df):
    file_path = "flats.xlsx"
    if new_df is None or new_df.empty:
        print("❌ Нет новых данных для объединения")
        return pd.DataFrame()

    if os.path.exists(file_path):
        try:
            old_df = pd.read_excel(file_path)
            merged = pd.concat([old_df, new_df], ignore_index=True).drop_duplicates(
                subset=('ЖК, оч. и корп.', '№'), keep="last")
            return merged
        except Exception as e:
            print(f"⚠️ Ошибка при чтении старого файла: {e}. Создаём новый.")
            return new_df
    else:
        return new_df


# === Основная GUI логика ===
def main():
    os.makedirs("data", exist_ok=True)

    root = tk.Tk()
    root.title("Парсер nmarket.pro")
    root.geometry("600x550")
    root.resizable(False, False)

    # === Поля ввода ===
    ttk.Label(root, text="Логин:").pack(pady=5)
    entry_login = ttk.Entry(root, width=40)
    entry_login.pack()
    entry_login.insert(0, LOGIN)

    ttk.Label(root, text="Пароль:").pack(pady=5)
    entry_password = ttk.Entry(root, show="*", width=40)
    entry_password.pack()
    entry_password.insert(0, PASSWORD)

    ttk.Label(root, text="Ссылка для парсинга:").pack(pady=5)
    entry_url = ttk.Entry(root, width=40)
    entry_url.pack()

    ttk.Label(root, text="Количество страниц:").pack(pady=5)
    entry_pages = ttk.Entry(root, width=40)
    entry_pages.pack()
    entry_pages.insert(0, "50")

    # === История ссылок ===
    history_frame = ttk.Frame(root)
    history_frame.pack(pady=5)
    ttk.Label(history_frame, text="История ссылок:").pack(anchor="w")
    history_list = ScrolledText(history_frame, width=50, height=5, wrap=tk.WORD, state="disabled")
    history_list.pack()

    def update_history_display():
        history_list.config(state="normal")
        history_list.delete("1.0", tk.END)
        for line in load_history():
            history_list.insert(tk.END, line + "\n")
        history_list.config(state="disabled")

    update_history_display()

    # === Прогресс-бар и метки ===
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    progress_bar.pack(pady=10)

    current_page_label = ttk.Label(root, text="Текущая страница: 1", foreground="blue")
    current_page_label.pack(pady=5)

    result_label = ttk.Label(root, text="", foreground="green")
    result_label.pack()

    # === Запуск парсинга в отдельном потоке ===
    def start_parsing():
        login = entry_login.get()
        password = entry_password.get()
        url = entry_url.get()

        try:
            max_pages = int(entry_pages.get())
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректное число для количества страниц.")
            return

        if not login or not password or not url:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        result_label.config(text="Идёт обработка...")
        progress_bar["value"] = 0
        current_page_label.config(text="Текущая страница: 1")

        def update_progress(value):
            progress_bar["value"] = value

        def update_result(success, message):
            if success:
                result_label.config(text="✅ Парсинг завершён. Данные сохранены.")
            else:
                result_label.config(text=message)
            update_history_display()

        def threaded_run():
            all_data = pd.DataFrame()
            page_counter = 1
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            try:
                # Авторизация
                driver.get("https://auth.nmarket.pro/Account/Login ")
                WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "По логину")]'))
                ).click()
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, "login-input"))
                ).send_keys(login)
                driver.find_element(By.ID, "mat-input-2").send_keys(password)
                WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.ID, "login_username_click"))
                ).click()
                time.sleep(3)

                # Переход на первую страницу
                current_url = url
                driver.get(current_url)
                print(f"Открыта первая страница: {current_url}")
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".apartment-grid__table-tbody"))
                )

                while True:
                    html = driver.page_source
                    df = parse_data(html)
                    if not df.empty:
                        all_data = pd.concat([all_data, df], ignore_index=True)

                    # Обновление интерфейса
                    root.after(100, update_progress, min(100, int(page_counter * (100 / max_pages))))
                    root.after(100, lambda p=page_counter: current_page_label.config(text=f"Текущая страница: {p}"))

                    # Промежуточное сохранение
                    if page_counter % 5 == 0:
                        temp_filename = os.path.join("data", f"flats_page_{page_counter}.xlsx")
                        save_to_excel_with_images(all_data, filename=temp_filename)

                    if page_counter >= max_pages:
                        print("🛑 Достигнут лимит страниц.")
                        break

                    # Логика перехода на следующую страницу
                    try:
                        # Получаем текущий номер активной страницы
                        current_page_element = driver.find_element(By.CSS_SELECTOR, '.pagination__active')
                        current_page = int(current_page_element.text.strip())

                        # Ищем кнопку "Далее"
                        next_button = WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, '.pagination__next-button'))
                        )
                        driver.execute_script("arguments[0].click();", next_button)

                        # Ожидаем обновления номера страницы
                        WebDriverWait(driver, 15).until(
                            lambda d: int(d.find_element(By.CSS_SELECTOR, '.pagination__active').text.strip()) > current_page
                        )

                        # Успешный переход
                        page_counter += 1
                        print(f"✅ Успешно перешли на страницу {page_counter}")

                    except TimeoutException:
                        print("🔚 Достигнута последняя страница")
                        break
                    except Exception as e:
                        print(f"❌ Ошибка перехода: {str(e)}")
                        break

                # Финализация данных
                sorting_df = merge_new_data(all_data)
                save_to_excel_with_images(sorting_df)
                save_history(entry_url.get())

                root.after(100, update_progress, 100)
                root.after(100, update_result, True, "✅ Парсинг завершён. Данные сохранены.")

            except Exception as e:
                root.after(100, update_result, False, f"❌ Ошибка: {str(e)}")
            finally:
                driver.quit()

        threading.Thread(target=threaded_run, daemon=True).start()

    ttk.Button(root, text="Начать парсинг", command=start_parsing).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()