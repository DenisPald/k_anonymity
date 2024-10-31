import csv
from collections import Counter

def read_input_file(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = list(reader)
    return data

def save_data(file_path, data):
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def get_quasi_identifiers(data, quasi_identifiers):
    return list(map(lambda row: {key: row[key] for key in quasi_identifiers}, data))

def is_male(name:str) -> bool:
    return name.split()[0][-1] != 'а'

def local_generalization_of_cost(data):
    def generalize_cost(cost):
        cost = int(cost)
        if cost < 3000:
            lower_bound = (cost // 50) * 50  # Округление вниз до 100
            upper_bound = lower_bound + 50     # Округление вверх до 100
            return f"От {lower_bound} до {upper_bound}"
        if cost < 5000:
            lower_bound = (cost // 100) * 100  # Округление вниз до 500
            upper_bound = lower_bound + 100     # Округление вверх до 500
            return f"От {lower_bound} до {upper_bound}"
        if cost < 10_000:
            lower_bound = (cost // 1000) * 1000  # Округление вниз до 500
            upper_bound = lower_bound + 1000     # Округление вверх до 500
        return f"От 10_000"

    return list(map(lambda row: {**row, **{'Стоимость': generalize_cost(row['Стоимость'])}}, data))

def pseudonymize_name(data):
    def change_name(name):
        if is_male(name):
            return 'Мужское имя'
        else:
            return 'Женское имя'

    return list(map(lambda row: {**row, **{'ФИО': change_name(row['ФИО'])}}, data))

def local_generalization_of_card(data):
    def generalize_card(value:str):
        reverse_cards_bin = {
            220100: "Мир",
            400680: "Visa",
            546947: "Mastercard",
            220070: "Мир",
            437772: "Visa",
            513990: "Mastercard",
            220001: "Мир",
            411927: "Visa",
            521155: "Mastercard"
        }
        card_bin_len = 6
        card_bin_value = int(value[0:card_bin_len])
        return reverse_cards_bin[card_bin_value] 
    
    return list(map(lambda row: {**row, **{'Карта оплаты': generalize_card(row['Карта оплаты'])}}, data))


def local_generalization_of_datetime(data):
    def generalize_value(value:str):
        len_of_date_data = 10
        return value[0:len_of_date_data]
    
    return list(map(lambda row: {**row, **{'Дата отъезда': generalize_value(row['Дата отъезда']), 'Дата приезда': generalize_value(row['Дата приезда'])}}, data))

def pseudonymize_route(data):
    def pseudonymize_value(value:str):
        if value[-1].isdigit():
            return "Сапсан"
        else:
            return "Ласточка"
    
    return list(map(lambda row: {**row, **{'Рейс': pseudonymize_value(row['Рейс'])}}, data))

def remove_column(data, column):
    return list(map(lambda row: {key: row[key] for key in row if key != column}, data))

def calculate_k_anonymity(data, quasi_identifiers):
    quasi_rows = get_quasi_identifiers(data, quasi_identifiers)
    counter = Counter(tuple(row.items()) for row in quasi_rows)
    return min(counter.values()), counter

def find_low_k_anonymity(counter, threshold=10):
    bad_k_values = {k: v for k, v in counter.items() if v < threshold}
    return bad_k_values

def compare_datasets(original, anonymized, quasi_identifiers):
    original_unique = set(tuple(row.items()) for row in get_quasi_identifiers(original, quasi_identifiers))
    anonymized_unique = set(tuple(row.items()) for row in get_quasi_identifiers(anonymized, quasi_identifiers))
    return len(original_unique), len(anonymized_unique), len(anonymized_unique) / len(original_unique) * 100

def anonymize_data(data, quasi_identifiers):
    k_value, counter = calculate_k_anonymity(data, quasi_identifiers)

    anonymized_data = local_generalization_of_cost(data)
    anonymized_data = pseudonymize_name(anonymized_data)
    anonymized_data = local_generalization_of_card(anonymized_data)
    anonymized_data = remove_column(anonymized_data, 'Паспорт')
    anonymized_data = remove_column(anonymized_data, 'Вагон и место')
    anonymized_data = pseudonymize_route(anonymized_data)
    anonymized_data = local_generalization_of_datetime(anonymized_data)

    # Локальное подавление строк с низким k_anonimity
    k_value, counter = calculate_k_anonymity(anonymized_data, quasi_identifiers)
    low_k_entries = find_low_k_anonymity(counter)
    suppressed_data = []
    for row in anonymized_data:
        quasi_id_tuple = tuple((key, row[key]) for key in quasi_identifiers)
        if quasi_id_tuple in low_k_entries:
            # Применяем подавление (заменяем значения квази-идентификаторов на обобщённое значение)
            suppressed_row = {**row}
            for key in quasi_identifiers:
                suppressed_row[key] = 'ПОДАВЛЕНО'
            row = suppressed_row

    # Расчет итогового k_anonimity, полезности данных
    k_value, counter = calculate_k_anonymity(suppressed_data, quasi_identifiers)
    len_of_dataset = len(data)
    least_common = [(value, 100*value/len_of_dataset) for _, value in counter.most_common()[:-6:-1]]
    original_unique, anonymized_unique, usefulness = compare_datasets(data, suppressed_data, quasi_identifiers)

    return suppressed_data, least_common, usefulness

def calculate_input_k_anonymity(file_path, quasi_identifiers):
    data = read_input_file(file_path)
    k_value, counter = calculate_k_anonymity(data, quasi_identifiers)
    least_common = [value for _, value in counter.most_common()[:-6:-1]]
    return k_value, least_common

