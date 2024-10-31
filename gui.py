import tkinter as tk
from tkinter import filedialog, messagebox
from main import anonymize_data, calculate_k_anonymity, save_data, read_input_file, compare_datasets

# Глобальные переменные для анонимизированных данных и оригинальных данных
anonymized_dataset = None
original_dataset = None

def select_input_file(entry_field):
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, file_path)

    
    global original_dataset
    original_dataset = read_input_file(file_path)

def run_anonymization():
    try:
        global original_dataset
        if original_dataset:
            quasi_ids = [var.get() for var in quasi_identifiers if var.get()]
            anonymized_data, least_common, usefulness = anonymize_data(original_dataset, quasi_ids)

            # Обновляем поля
            k_anonymity_text.delete(1.0, tk.END)
            k_anonymity_text.insert(tk.END, f"{least_common[0][0]}")

            least_common_text.delete(1.0, tk.END)
            text = ""
            for value in least_common:
                text += f"{value[0]}({value[1]:.3f}%) "
            least_common_text.insert(tk.END, text)
            
            usefulness_text.delete(1.0, tk.END)
            usefulness_text.insert(tk.END, f"{usefulness:.2f}%")

            global anonymized_dataset
            anonymized_dataset = anonymized_data
        else:
            messagebox.showerror("Ошибка", "Сначала введите данные")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при анонимизации: {str(e)}")

def recalculate_k_anonymity():
    try:
        global anonymized_dataset, original_dataset
        if anonymized_dataset:
            quasi_ids = [var.get() for var in quasi_identifiers if var.get()]
            k_value, counter = calculate_k_anonymity(anonymized_dataset, quasi_ids)
            len_of_dataset = len(anonymized_dataset)
            least_common = [(value, 100*value/len_of_dataset) for _, value in counter.most_common()[:-6:-1]]

            original_unique, anonymized_unique, usefulness = compare_datasets(original_dataset, anonymized_dataset, quasi_ids)

            # Обновляем поля
            k_anonymity_text.delete(1.0, tk.END)
            k_anonymity_text.insert(tk.END, str(k_value))

            least_common_text.delete(1.0, tk.END)
            text = ""
            for value in least_common:
                text += f"{value[0]}({value[1]:.3f}%) "
            least_common_text.insert(tk.END, text)

            usefulness_text.delete(1.0, tk.END)
            usefulness_text.insert(tk.END, f"{usefulness:.2f}%")
        elif original_dataset:
            quasi_ids = [var.get() for var in quasi_identifiers if var.get()]
            k_value, counter = calculate_k_anonymity(original_dataset, quasi_ids)
            len_of_dataset = len(original_dataset)
            least_common = [(value, 100*value/len_of_dataset) for _, value in counter.most_common()[:-6:-1]]

            # Обновляем поля
            k_anonymity_text.delete(1.0, tk.END)
            k_anonymity_text.insert(tk.END, str(k_value))

            least_common_text.delete(1.0, tk.END)
            text = ""
            for value in least_common:
                text += f"{value[0]}({value[1]:.3f}%) "
            least_common_text.insert(tk.END, text)

            usefulness_text.delete(1.0, tk.END)
            usefulness_text.insert(tk.END, "N/A (Полезность рассчитывается только для анонимизированных данных)")
        else:
            messagebox.showwarning("Предупреждение", "Сначала введите данные.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при пересчете k-анонимности: {str(e)}")

def save_anonymized_data():
    try:
        global anonymized_dataset
        if anonymized_dataset:
            save_as_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if save_as_file:
                save_data(save_as_file, anonymized_dataset)
                messagebox.showinfo("Сохранено", "Анонимизированные данные успешно сохранены")
        else:
            messagebox.showwarning("Предупреждение", "Сначала выполните анонимизацию данных.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при сохранении анонимизированных данных: {str(e)}")

# Окно GUI
root = tk.Tk()
root.title("Анонимизация данных")

# Поле для выбора входного файла
tk.Label(root, text="Имя входного файла:").grid(row=0, column=0)
input_file_entry = tk.Entry(root, width=40)
input_file_entry.grid(row=0, column=1)
input_file_btn = tk.Button(root, text="Выбрать файл", command=lambda: select_input_file(input_file_entry))
input_file_btn.grid(row=0, column=2)

# Выбор квази-идентификаторов
quasi_identifiers_names = ['ФИО', 'Откуда', 'Куда', 'Дата отъезда', 'Дата приезда', 'Карта оплаты', 'Стоимость', 'Рейс']
quasi_identifiers = []
tk.Label(root, text="Квази-идентификаторы:").grid(row=1, column=0)

for i, quasi_id in enumerate(quasi_identifiers_names):
    var = tk.StringVar(value=quasi_id)  # Устанавливаем по умолчанию все квази-идентификаторы
    cb = tk.Checkbutton(root, text=quasi_id, variable=var, onvalue=quasi_id, offvalue="")
    cb.grid(row=2 + i, column=0, sticky="w")
    quasi_identifiers.append(var)

# Поля для вывода результата
tk.Label(root, text="Значение k-анонимности:").grid(row=11, column=0)
k_anonymity_text = tk.Text(root, height=1, width=40)
k_anonymity_text.grid(row=11, column=1)

tk.Label(root, text="Топ худших k-анонимности:").grid(row=12, column=0)
least_common_text = tk.Text(root, height=1, width=40)
least_common_text.grid(row=12, column=1)

tk.Label(root, text="Полезность:").grid(row=13, column=0)
usefulness_text = tk.Text(root, height=1, width=40)
usefulness_text.grid(row=13, column=1)

# Кнопки
anonymize_btn = tk.Button(root, text="Анонимизировать", command=run_anonymization)
anonymize_btn.grid(row=15, column=0)

recalculate_k_btn = tk.Button(root, text="Посчитать k-анонимность", command=recalculate_k_anonymity)
recalculate_k_btn.grid(row=15, column=1)

save_anonymized_btn = tk.Button(root, text="Сохранить анонимизированные данные", command=save_anonymized_data)
save_anonymized_btn.grid(row=16, column=0)

root.mainloop()
