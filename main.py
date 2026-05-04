import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# --- Основная логика приложения ---
class TrainingPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x500")

        # Переменные для фильтрации
        self.filter_type_var = tk.StringVar()
        self.filter_date_var = tk.StringVar()

        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка данных при запуске
        self.load_data()

    def create_widgets(self):
        # --- Блок ввода данных ---
        frame_input = ttk.LabelFrame(self.root, text="Добавить тренировку", padding="10")
        frame_input.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        ttk.Label(frame_input, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", pady=2)
        self.date_entry = ttk.Entry(frame_input, width=20)
        self.date_entry.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(frame_input, text="Тип тренировки:").grid(row=1, column=0, sticky="w", pady=2)
        self.type_entry = ttk.Entry(frame_input, width=20)
        self.type_entry.grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(frame_input, text="Длительность (мин):").grid(row=2, column=0, sticky="w", pady=2)
        self.duration_entry = ttk.Entry(frame_input, width=20)
        self.duration_entry.grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Button(frame_input, text="Добавить тренировку", command=self.add_training).grid(
            row=3, column=0, columnspan=2, pady=10)

        # --- Блок фильтрации ---
        frame_filter = ttk.LabelFrame(self.root, text="Фильтр", padding="10")
        frame_filter.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        ttk.Label(frame_filter, text="По типу:").grid(row=0, column=0, sticky="w")
        self.filter_type_entry = ttk.Entry(frame_filter, textvariable=self.filter_type_var)
        self.filter_type_entry.grid(row=0, column=1, sticky="ew")

        ttk.Label(frame_filter, text="По дате:").grid(row=1, column=0, sticky="w")
        self.filter_date_entry = ttk.Entry(frame_filter, textvariable=self.filter_date_var)
        self.filter_date_entry.grid(row=1, column=1, sticky="ew")

        ttk.Button(frame_filter, text="Применить фильтр", command=self.apply_filter).grid(
            row=2, column=0, columnspan=2, pady=(5, 0))
        
        ttk.Button(frame_filter, text="Сбросить фильтр", command=self.reset_filter).grid(
            row=3, column=0, columnspan=2, pady=(5, 0))

        # --- Таблица (Treeview) ---
        self.tree = ttk.Treeview(self.root, columns=("date", "type", "duration"), show='headings')
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип")
        self.tree.heading("duration", text="Длительность (мин)")
        
        self.tree.column("date", anchor="center", width=150)
        self.tree.column("type", anchor="center", width=350)
        self.tree.column("duration", anchor="center", width=150)
        
        self.tree.grid(row=4, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="nsew")

        # --- Блок управления данными (JSON) ---
        frame_json = ttk.Frame(self.root)
        frame_json.grid(row=5, column=0, columnspan=2)

        ttk.Button(frame_json, text="Сохранить в JSON", command=self.save_data).grid(
            row=0, column=0, padx=(10, 5), pady=(0, 10))
        
        ttk.Button(frame_json, text="Загрузить из JSON", command=self.load_data).grid(
            row=0, column=1, padx=(5, 10), pady=(0, 10))

    # --- Логика добавления тренировки ---
    def add_training(self):
        date_str = self.date_entry.get().strip()
        type_str = self.type_entry.get().strip()
        duration_str = self.duration_entry.get().strip()

        is_valid, error_msg = self.validate_inputs(date_str, duration_str)
        
        if not is_valid:
            messagebox.showerror("Ошибка валидации", error_msg)
            return

        # Если валидация пройдена — добавляем в таблицу
        self.tree.insert("", "end", values=(date_str, type_str, duration_str))
        
        # Очищаем поля ввода после добавления
        self.date_entry.delete(0, tk.END)
        self.type_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)
        
    def validate_inputs(self, date_str: str, duration_str: str):
        try:
            datetime.strptime(date_str.strip(), "%Y-%m-%d")
            duration = float(duration_str.strip())
            if duration <= 0:
                return False, "Длительность должна быть положительным числом."
            return True, ""
        except ValueError as e:
            if "time data" in str(e):
                return False, "Неверный формат даты. Используйте ГГГГ-ММ-ДД."
            else:
                return False, "Длительность должна быть числом."
    
    # --- Логика фильтрации ---
    def apply_filter(self):
       filter_type = self.filter_type_var.get().lower()
       filter_date = self.filter_date_var.get()
       
       for child in self.tree.get_children():
           values = self.tree.item(child)['values']
           date_match = (not filter_date) or (values[0] == filter_date)
           type_match = (not filter_type) or (filter_type in values[1].lower())
           
           if date_match and type_match:
               self.tree.item(child, tags='show')
           else:
               self.tree.item(child, tags='hide')
       self.tree.tag_configure('hide', elide=True) 
    
    def reset_filter(self):
       self.filter_type_var.set("")
       self.filter_date_var.set("")
       for child in self.tree.get_children():
           self.tree.item(child, tags='')
       self.tree.tag_configure('hide', elide=True) 
    
    # --- Логика работы с JSON ---
    def save_data(self):
       data = [self.tree.item(child)['values'] for child in self.tree.get_children()]
       try:
           with open('trainings.json', 'w', encoding='utf-8') as f:
               json.dump(data, f, ensure_ascii=False, indent=4)
           messagebox.showinfo("Успех", "Данные успешно сохранены в trainings.json")
       except Exception as e:
           messagebox.showerror("Ошибка сохранения", str(e))
    
    def load_data(self):
       if not os.path.exists('trainings.json'):
           return

       try:
           with open('trainings.json', 'r', encoding='utf-8') as f:
               data = json.load(f)
           
           # Очищаем текущую таблицу перед загрузкой
           for child in self.tree.get_children():
               self.tree.delete(child)
           
           for row in data:
               if len(row) == 3: 
                   self.tree.insert("", "end", values=tuple(row))
       except Exception as e:
           messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить данные: {e}")

# --- Запуск приложения ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlannerApp(root)
    root.mainloop()
