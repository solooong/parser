from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import pandas as pd
import os
import requests
from openpyxl.drawing.image import Image as XLImage
from io import BytesIO
import tkinter as tk
from tkinter import ttk, messagebox
# Настройки браузера
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Автоматическая загрузка правильного ChromeDriver
service = Service(ChromeDriverManager().install())
# Запуск браузера
driver = webdriver.Chrome(service=service, options=chrome_options)
# Данные для входа
LOGIN = "laguta@nian.tv"
PASSWORD = "614084"


# 2. Получить ссылку от пользователя
def get_user_link():
    return input("Введите ссылку на объявления: ")

# 3. Загрузить страницу
def load_page(url):
    driver.get(url)
    time.sleep(5)  # ждём загрузки JS
    return driver.page_source

# 4. Парсинг данных
def parse_data(html):
    soup = BeautifulSoup(html, "lxml")
    table_body = soup.select_one(".apartment-grid__table-tbody")
    if not table_body:
        print("❌ Таблица объявлений не найдена")
        return None, []
    headers = []
    for th in soup.select(".apartment-grid__table-th"):
        label_span = th.select_one(".apartment-grid-sort-button__label")
        if label_span:
            headers.append(label_span.text.strip())
    headers.append("Ссылка")  # Гиперссылка
    data = []
 
    rows = table_body.select("tr.apartment-grid__table-tr")
    for row in rows:
        # Только нужные td
        cols = row.select("td.apartment-grid__table-td:not(.apartment-grid__table-td-image)")
        cols_text = [col.get_text(strip=True) for col in cols]

        # Удалить лишние столбцы (например, второй)
        if len(cols_text) >0:
            cols_text.pop(0)  # удалить лишний столбец

        # Поиск ссылки
        link_container = row.select_one("a")
        full_link = link_container.get("href", "") if link_container else ""

        # Получаем изображение
  
        # Добавляем ссылку
        cols_text.append(full_link)
        data.append(cols_text)
        
        # Проверка длины
        if len(cols_text) != len(headers):
            print(f"⚠️ Пропущена строка: {len(cols_text)} столбцов, ожидалось {len(headers)}")
            continue
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Заголовки:", headers)
        print("Пример строки:", cols_text)  
        data.append(cols_text)

    return pd.DataFrame(data, columns=headers)
# 5. Сохранение в Excel
def save_to_excel(df, filename="flats.xlsx"):
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"Данные сохранены в {filename}")

print("Ожидаем загрузку страницы...")
def main(login, password, parse_url):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        # Авторизация
        driver.get("https://auth.nmarket.pro/Account/Login ")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="mat-tab-label-content" and contains(text(), "По логину")]'))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-input"))
        ).send_keys(login)
        driver.find_element(By.ID, "mat-input-2").send_keys(password)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "login_username_click"))
        ).click()
        time.sleep(3)
        driver.get("https://nsk.nmarket.pro/ ")
        time.sleep(2)
        driver.get(parse_url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".apartment-grid__table-tbody"))
        )
        html = driver.page_source
        df=  parse_data(html)  
        save_to_excel(df)
    finally:
        driver.quit()

def run_parser():
    login = entry_login.get()
    password = entry_password.get()
    url = entry_url.get()
    if not login or not password or not url:
        messagebox.showwarning("Ошибка", "Заполните все поля!")
        return
    result_label.config(text="Идёт обработка...")
    # Вызываем основную функцию парсинга
    try:
        main(login, password, url)
        result_label.config(text="✅ Парсинг завершён. Файл сохранён.")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
        result_label.config(text="❌ Ошибка")


# Создаем окно
root = tk.Tk()
root.title("Парсер nmarket.pro")
root.geometry("500x300")
# Логин
ttk.Label(root, text="Логин:").pack(pady=5)
entry_login = ttk.Entry(root, width=40)
entry_login.pack()
entry_login.insert(0,LOGIN)
# Пароль
ttk.Label(root, text="Пароль:").pack(pady=5)
entry_password = ttk.Entry(root, show="*", width=40)
entry_password.pack()
entry_password.insert(0,PASSWORD)
# Ссылка
ttk.Label(root, text="Ссылка для парсинга:").pack(pady=5)
entry_url = ttk.Entry(root, width=40)
entry_url.pack()
# Кнопка запуска
run_button = ttk.Button(root, text="Запустить парсер", command=run_parser)
run_button.pack(pady=10)
# Результат
result_label = ttk.Label(root, text="", foreground="green")
result_label.pack()
# Запуск интерфейса
root.mainloop()