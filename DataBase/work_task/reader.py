import re
from pprint import pprint

import pdfplumber
import pandas as pd


def reading_bulletin_by_text_xls(xls_path: str) -> list[dict]:
    df = pd.read_excel(xls_path, header=None)
    date = ''

    # Находим строку с заголовками (где есть 'Код\nИнструмента')
    header_row = None
    for i in range(len(df)):
        if "Дата торгов:" in df.iloc[i, 1]:
            date = df.iloc[i, 1][-10::].strip()
        if df.iloc[i, 1] == 'Код\nИнструмента':
            header_row = i
            break

    # Устанавливаем заголовки из найденной строки
    headers = df.iloc[header_row].values

    data_df = df.iloc[header_row + 1:].copy()
    data_df.columns = headers

    column_mapping = {
        'Код\nИнструмента': 'exchange_product_id',
        'Наименование\nИнструмента': 'exchange_product_name',
        'Базис\nпоставки': 'delivery_basis_name',
        'Объем\nДоговоров\nв единицах\nизмерения': 'volume',
        'Обьем\nДоговоров,\nруб.': 'total',
        'Количество\nДоговоров,\nшт.': 'count'
    }

    # Переименовываем существующие колонки
    for old_name, new_name in column_mapping.items():
        if old_name in data_df.columns:
            data_df.rename(columns={old_name: new_name}, inplace=True)

    data_df = data_df.dropna(subset=['exchange_product_id'])
    data_df = data_df[~data_df['exchange_product_id'].astype(str).str.contains('Итого', na=False)]

    for col in ['volume', 'total', 'count']:
        if col in data_df.columns:
            data_df[col] = data_df[col].replace('-', pd.NA)
            data_df[col] = pd.to_numeric(data_df[col], errors='coerce')

    if 'count' in data_df.columns:
        data_df = data_df[data_df['count'] > 0]

    data_df = data_df.fillna('')

    # Очищаем строки от лишних пробелов
    data_df['exchange_product_id'] = data_df['exchange_product_id'].astype(str).str.strip()
    data_df['exchange_product_name'] = data_df['exchange_product_name'].astype(str).str.strip()
    data_df['delivery_basis_name'] = data_df['delivery_basis_name'].astype(str).str.strip()

    data_dict = data_df.to_dict('records')

    keys = (
        'count',
        'delivery_basis_name',
        'exchange_product_id',
        'exchange_product_name',
        'total',
        'volume',
        )
    result = []
    for line in data_dict:
        clear_data = dict()
        for key, value in line.items():
            if key not in keys:
                continue
            clear_data[key] = value
        clear_data["date"] = date
        result.append(clear_data)

    return result


def clear_data_pdf(pdf_path: str) -> tuple[list, str]:
    data = []
    date = ''

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            line = text.split('\n')
            data.append(line)

        for text in data:
            for num, line in enumerate(text):
                if "Дата торгов:" in line:
                    date = line[-10:-1].strip()
                if 'Единица измерения: Метрическая тонна' in line:
                    result = data[0][num::]
                    break

        for i in range(1, len(data)):
            result.extend(data[i])
        result = result[result.index('предложение спрос') + 1::]
    return result, date


def reading_bulletin_by_text_pdf(pdf_path: str) -> list[dict]:
    """Извлекает данные построчно из текста"""
    clear_data, date = clear_data_pdf(pdf_path)
    result_dict = []
    for line in clear_data:
        if line.endswith("станций"):
            line = line.replace("станций", "")
        if not line or len(line) < 1:
            continue
        if line[-1] != '0' and line[-1] != "-":
            code_match = re.match(r'^([A-Z0-9]+)', line)
            if not code_match:
                continue
            code = code_match.group(1)
            numbers = line.split()[-11::]
            numbers = [float(n.replace(' ', '')) for n in numbers if n.strip().isdigit()]
            if len(numbers) >= 3:
                volume = numbers[0]
                total = numbers[1]
                count = numbers[-1]

                # Извлекаем наименование (всё между кодом и числами)
                name_match = re.search(r'^[A-Z0-9]+\s+(.+?)\s+\d', line)
                name_part = name_match.group(1).strip() if name_match else ""

                # Пытаемся отделить базис по последней запятой
                if ',' in name_part:
                    parts = name_part.rsplit(',', 1)
                    name = parts[0].strip()
                    basis = parts[1].strip()
                else:
                    name = name_part
                    basis = ""

                if count > 0:
                    result_dict.append({
                        'exchange_product_id': code,
                        'exchange_product_name': name,
                        'delivery_basis_name': basis,
                        'volume': volume,
                        'total': total,
                        'count': count,
                        'date': date,
                    })
    return result_dict
