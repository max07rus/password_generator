import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500


class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)

        self.history_path = "history.json"
        self.history = []

        self.symbols = {
            "digits": string.digits,
            "letters": string.ascii_letters,
            "special": "!@#$%^&*()_+-=[]{}|;:,.<>?",
        }

        self.create_widgets()
        self.load_history()

    def create_widgets(self):
        frame_controls = tk.LabelFrame(self.root, text="Параметры пароля", padx=10, pady=10)
        frame_controls.pack(fill="x", padx=10, pady=5)

        self.length_label = tk.Label(frame_controls, text="Длина пароля (4–64):")
        self.length_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.length_var = tk.IntVar(value=12)
        self.length_slider = tk.Scale(
            frame_controls,
            from_=4,
            to=64,
            orient="horizontal",
            variable=self.length_var,
            length=200,
        )
        self.length_slider.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        self.digits_var = tk.BooleanVar(value=True)
        self.letters_var = tk.BooleanVar(value=True)
        self.special_var = tk.BooleanVar(value=True)

        self.cb_digits = tk.Checkbutton(
            frame_controls, text="Цифры (0-9)", variable=self.digits_var
        )
        self.cb_digits.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.cb_letters = tk.Checkbutton(
            frame_controls, text="Буквы (a-Z)", variable=self.letters_var
        )
        self.cb_letters.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.cb_special = tk.Checkbutton(
            frame_controls, text="Спецсимволы", variable=self.special_var
        )
        self.cb_special.grid(row=1, column=2, sticky="w", padx=5, pady=2)

        self.btn_generate = tk.Button(
            frame_controls, text="Сгенерировать", command=self.generate_password
        )
        self.btn_generate.grid(row=2, column=0, columnspan=3, pady=10)

        self.result_frame = tk.LabelFrame(self.root, text="Сгенерированный пароль", padx=10, pady=10)
        self.result_frame.pack(fill="x", padx=10, pady=5)
        self.result_var = tk.StringVar()
        self.result_entry = tk.Entry(
            self.result_frame,
            textvariable=self.result_var,
            font=("Courier", 11),
            state="readonly",
            width=30,
        )
        self.result_entry.pack(padx=5, pady=5)
        self.btn_copy = tk.Button(
            self.result_frame, text="Копировать в буфер", command=self.copy_to_clipboard
        )
        self.btn_copy.pack(pady=5)

        frame_history = tk.LabelFrame(self.root, text="История генераций", padx=10, pady=10)
        frame_history.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("password", "length", "digits", "letters", "special", "created_at")
        self.tree = ttk.Treeview(
            frame_history,
            columns=columns,
            show="headings",
            height=8,
            selectmode="browse",
        )

        headers = {
            "password": "Пароль",
            "length": "Длина",
            "digits": "Цифры",
            "letters": "Буквы",
            "special": "Спец.",
            "created_at": "Дата и время",
        }
        widths = {
            "password": 120,
            "length": 60,
            "digits": 60,
            "letters": 60,
            "special": 60,
            "created_at": 140,
        }

        for col, text in headers.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=widths[col])

        vsb = ttk.Scrollbar(frame_history, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frame_history, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        frame_history.grid_rowconfigure(0, weight=1)
        frame_history.grid_columnconfigure(0, weight=1)

    def get_chars(self):
        chars = ""
        if self.digits_var.get():
            chars += self.symbols["digits"]
        if self.letters_var.get():
            chars += self.symbols["letters"]
        if self.special_var.get():
            chars += self.symbols["special"]
        return chars

    def generate_password(self):
        length = self.length_var.get()
        chars = self.get_chars()

        if not chars:
            messagebox.showwarning("Ошибка", "Выберите хотя бы один тип символов.")
            return
        if length < 4:
            messagebox.showwarning("Ошибка", "Минимальная длина — 4 символа.")
            return
        if length > 64:
            messagebox.showwarning("Ошибка", "Максимальная длина — 64 символа.")
            return

        password = "".join(random.choice(chars) for _ in range(length))
        self.result_var.set(password)

        record = {
            "password": password,
            "length": length,
            "digits": self.digits_var.get(),
            "letters": self.letters_var.get(),
            "special": self.special_var.get(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.history.append(record)
        self.add_record_to_tree(record)
        self.save_history()

    def add_record_to_tree(self, record):
        values = (
            record["password"],
            record["length"],
            "Да" if record["digits"] else "Нет",
            "Да" if record["letters"] else "Нет",
            "Да" if record["special"] else "Нет",
            record["created_at"],
        )
        self.tree.insert("", 0, values=values)

    def copy_to_clipboard(self):
        password = self.result_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Копирование", "Пароль скопирован в буфер обмена.")

    def load_history(self):
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.history = data
                        for record in data:
                            self.add_record_to_tree(record)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {e}")

    def save_history(self):
        try:
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")


if __name__ == "__main__":
    app = PasswordGeneratorApp(tk.Tk())
    app.root.mainloop()
