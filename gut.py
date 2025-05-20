import tkinter as tk
from tkinter import ttk, filedialog, messagebox
# Импортируем ваши модули
import parser
import sorting
import search

# --- Справочники для выпадающих списков ---
districts = {
    215: 'Октябрьский',
    213: 'Кировский',
    209: 'Дзержинский',
    210: 'Железнодорожный',
    211: 'Заельцовский',
    214: 'Ленинский'
}
house_material_types = [
    "панельный", "кирпичный", "монолитный", "блочный", "деревянный", "другое"
]
sort_by_options = [
    "price_asc", "price_desc", "date_asc", "date_desc"
]

class RealtyParserGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Realty Parser & Analyzer")
        self.geometry("800x700")
        self.resizable(False, False)

        self.selected_action = tk.StringVar(value="parse")
        self.search_type = tk.StringVar(value="new")
        self.selected_file = tk.StringVar()
        self.metro_var = tk.StringVar()
        self.metro_station_var = tk.StringVar()
        self.district_var = tk.StringVar()
        self.house_material_var = tk.StringVar()
        self.sort_by_var = tk.StringVar()
        self.only_homeowner = tk.BooleanVar()
        self.have_loggia = tk.BooleanVar()
        self.only_flat = tk.BooleanVar()
        self.only_apartment = tk.BooleanVar()
        self.flat_share = tk.StringVar()
        self.filter_streets = tk.StringVar()
        self.city_var = tk.StringVar()
        self.search_jk_var = tk.StringVar()

        self.init_widgets()

    def init_widgets(self):
        # --- Выбор действия ---
        frame_action = ttk.LabelFrame(self, text="Выберите действие")
        frame_action.pack(fill="x", padx=10, pady=5)

        actions = [("Парсинг объявлений", "parse"),
                   ("Обработка данных (группировка)", "group"),
                   ("Поиск маркетинговых активностей", "search")]
        for text, val in actions:
            ttk.Radiobutton(frame_action, text=text, variable=self.selected_action, value=val, command=self.update_action).pack(side="left", padx=10)

        self.frame_parse = ttk.Frame(self)
        self.frame_group = ttk.Frame(self)
        self.frame_search = ttk.Frame(self)

        self.frame_parse.pack(fill="x", padx=10, pady=5)
        self.update_action()

    def update_action(self):
        for frame in [self.frame_parse, self.frame_group, self.frame_search]:
            frame.pack_forget()

        if self.selected_action.get() == "parse":
            self.show_parse()
        elif self.selected_action.get() == "group":
            self.show_group()
        elif self.selected_action.get() == "search":
            self.show_search()

    def show_parse(self):
        frame = self.frame_parse
        for widget in frame.winfo_children():
            widget.destroy()

        # --- Тип поиска ---
        ttk.Label(frame, text="Тип поиска:").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(frame, text="Поиск по новостройкам", variable=self.search_type, value="new").grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(frame, text="Поиск квартир по параметрам", variable=self.search_type, value="params").grid(row=0, column=2, sticky="w")

        row = 1
        ttk.Label(frame, text="Тип жилья:").grid(row=row, column=0, sticky="w")
        self.object_type_entry = ttk.Combobox(frame, values=["new", "secondary"], state="readonly")
        self.object_type_entry.current(0)
        self.object_type_entry.grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(frame, text="Первая страница:").grid(row=row, column=0, sticky="w")
        self.start_page_entry = ttk.Entry(frame)
        self.start_page_entry.insert(0, "1")
        self.start_page_entry.grid(row=row, column=1, sticky="w")

        ttk.Label(frame, text="Последняя страница:").grid(row=row, column=2, sticky="w")
        self.end_page_entry = ttk.Entry(frame)
        self.end_page_entry.insert(0, "20")
        self.end_page_entry.grid(row=row, column=3, sticky="w")

        row += 1
        ttk.Checkbutton(frame, text="Только собственники", variable=self.only_homeowner).grid(row=row, column=0, sticky="w")
        ttk.Label(frame, text="Цена от:").grid(row=row, column=1, sticky="w")
        self.min_price_entry = ttk.Entry(frame)
        self.min_price_entry.insert(0, "0")
        self.min_price_entry.grid(row=row, column=2, sticky="w")
        ttk.Label(frame, text="до:").grid(row=row, column=3, sticky="w")
        self.max_price_entry = ttk.Entry(frame)
        self.max_price_entry.insert(0, "30000000")
        self.max_price_entry.grid(row=row, column=4, sticky="w")

        row += 1
        ttk.Label(frame, text="Балконов от:").grid(row=row, column=0, sticky="w")
        self.min_balconies_entry = ttk.Entry(frame)
        self.min_balconies_entry.grid(row=row, column=1, sticky="w")
        ttk.Checkbutton(frame, text="Лоджия", variable=self.have_loggia).grid(row=row, column=2, sticky="w")

        row += 1
        ttk.Label(frame, text="Год постройки от:").grid(row=row, column=0, sticky="w")
        self.min_house_year_entry = ttk.Entry(frame)
        self.min_house_year_entry.grid(row=row, column=1, sticky="w")
        ttk.Label(frame, text="до:").grid(row=row, column=2, sticky="w")
        self.max_house_year_entry = ttk.Entry(frame)
        self.max_house_year_entry.grid(row=row, column=3, sticky="w")

        row += 1
        ttk.Label(frame, text="Этаж от:").grid(row=row, column=0, sticky="w")
        self.min_floor_entry = ttk.Entry(frame)
        self.min_floor_entry.grid(row=row, column=1, sticky="w")
        ttk.Label(frame, text="до:").grid(row=row, column=2, sticky="w")
        self.max_floor_entry = ttk.Entry(frame)
        self.max_floor_entry.grid(row=row, column=3, sticky="w")

        row += 1
        ttk.Label(frame, text="Этажей в доме от:").grid(row=row, column=0, sticky="w")
        self.min_total_floor_entry = ttk.Entry(frame)
        self.min_total_floor_entry.grid(row=row, column=1, sticky="w")
        ttk.Label(frame, text="до:").grid(row=row, column=2, sticky="w")
        self.max_total_floor_entry = ttk.Entry(frame)
        self.max_total_floor_entry.grid(row=row, column=3, sticky="w")

        row += 1
        ttk.Label(frame, text="Тип дома:").grid(row=row, column=0, sticky="w")
        self.house_material_combo = ttk.Combobox(frame, values=house_material_types, state="readonly")
        self.house_material_combo.grid(row=row, column=1, sticky="w")

        ttk.Label(frame, text="Район:").grid(row=row, column=2, sticky="w")
        self.district_combo = ttk.Combobox(frame, values=list(districts.values()), state="readonly")
        self.district_combo.grid(row=row, column=3, sticky="w")

        row += 1
        ttk.Label(frame, text="Станция метро:").grid(row=row, column=0, sticky="w")
        self.metro_station_entry = ttk.Entry(frame)
        self.metro_station_entry.grid(row=row, column=1, sticky="w")
        ttk.Label(frame, text="До метро пешком (мин):").grid(row=row, column=2, sticky="w")
        self.metro_foot_minute_entry = ttk.Entry(frame)
        self.metro_foot_minute_entry.grid(row=row, column=3, sticky="w")

        row += 1
        ttk.Label(frame, text="Только доли:").grid(row=row, column=0, sticky="w")
        self.flat_share_combo = ttk.Combobox(frame, values=["", "1 - только доли", "2 - без долей"], state="readonly")
        self.flat_share_combo.grid(row=row, column=1, sticky="w")
        ttk.Checkbutton(frame, text="Без апартаментов", variable=self.only_flat).grid(row=row, column=2, sticky="w")
        ttk.Checkbutton(frame, text="Только апартаменты", variable=self.only_apartment).grid(row=row, column=3, sticky="w")

        row += 1
        ttk.Label(frame, text="Сортировка:").grid(row=row, column=0, sticky="w")
        self.sort_by_combo = ttk.Combobox(frame, values=sort_by_options, state="readonly")
        self.sort_by_combo.grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Button(frame, text="Запустить парсинг", command=self.run_parser).grid(row=row, column=0, columnspan=2, pady=10)

        frame.pack(fill="x", padx=10, pady=5)

    def show_group(self):
        frame = self.frame_group
        for widget in frame.winfo_children():
            widget.destroy()

        ttk.Label(frame, text="Выберите файл для анализа (.xlsx):").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.selected_file, width=40, state="readonly").grid(row=0, column=1, sticky="w")
        ttk.Button(frame, text="Обзор...", command=self.select_file).grid(row=0, column=2, padx=5)

        ttk.Label(frame, text="Фильтр по улицам (через запятую):").grid(row=1, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.filter_streets, width=40).grid(row=1, column=1, sticky="w")

        ttk.Button(frame, text="Запустить группировку", command=self.run_grouping).grid(row=2, column=0, columnspan=2, pady=10)

        frame.pack(fill="x", padx=10, pady=5)

    def show_search(self):
        frame = self.frame_search
        for widget in frame.winfo_children():
            widget.destroy()

        ttk.Label(frame, text="Город поиска:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.city_var, width=30).grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="ЖК для поиска (через запятую):").grid(row=1, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.search_jk_var, width=50).grid(row=1, column=1, sticky="w")

        ttk.Button(frame, text="Запустить поиск", command=self.run_search).grid(row=2, column=0, columnspan=2, pady=10)

        frame.pack(fill="x", padx=10, pady=5)

    def select_file(self):
        file = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file:
            self.selected_file.set(file)

    def run_parser(self):
        if self.search_type.get() == "new":
            try:
                parser.new_dev()
                messagebox.showinfo("Парсинг завершен", "Парсинг новостроек завершен. Результат сохранен в папке result.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при парсинге новостроек:\n{e}")
        else:
            params = {
                "object_type": self.object_type_entry.get(),
                "start_page": int(self.start_page_entry.get()),
                "end_page": int(self.end_page_entry.get()),
                "is_by_homeowner": self.only_homeowner.get(),
                "min_price": int(self.min_price_entry.get()),
                "max_price": int(self.max_price_entry.get()),
                "min_balconies": self.min_balconies_entry.get() or None,
                "have_loggia": self.have_loggia.get(),
                "min_house_year": self.min_house_year_entry.get() or None,
                "max_house_year": self.max_house_year_entry.get() or None,
                "min_floor": self.min_floor_entry.get() or None,
                "max_floor": self.max_floor_entry.get() or None,
                "min_total_floor": self.min_total_floor_entry.get() or None,
                "max_total_floor": self.max_total_floor_entry.get() or None,
                "house_material_type": self.house_material_combo.get(),
                "district": self.district_combo.get(),
                "metro": None,
                "metro_station": self.metro_station_entry.get(),
                "metro_foot_minute": self.metro_foot_minute_entry.get() or None,
                "flat_share": self.flat_share_combo.get(),
                "only_flat": self.only_flat.get(),
                "only_apartment": self.only_apartment.get(),
                "sort_by": self.sort_by_combo.get()
            }
            try:
                result_file = parser.all_flar_search_gui(params)
                messagebox.showinfo("Парсинг завершен", f"Результат сохранен: {result_file}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при парсинге:\n{e}")

    def run_grouping(self):
        if not self.selected_file.get():
            messagebox.showerror("Ошибка", "Выберите файл для анализа!")
            return
        try:
            result_file = sorting.sorting(file_path=self.selected_file.get(), filter_streets=self.filter_streets.get())
            messagebox.showinfo("Группировка завершена", f"Результат сохранен: {result_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при группировке:\n{e}")

    def run_search(self):
        city = self.city_var.get()
        developers = [jk.strip() for jk in self.search_jk_var.get().split(",") if jk.strip()]
        try:
            search.main(city=city, developers=developers)
            messagebox.showinfo("Поиск завершен", "Поиск маркетинговых активностей завершен.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при поиске:\n{e}")

if __name__ == "__main__":
    app = RealtyParserGUI()
    app.mainloop()
