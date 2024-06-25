import pandas as pd
import re
import numpy as np
from collections import Counter
from nameparser import HumanName
import russiannames

# Загрузка данных из CSV
df = pd.read_csv('data.csv')

# Удаление дубликатов
df = df.drop_duplicates()

# Функция для извлечения количества комнат
def extract_room_count(title):
    match = re.search(r'(\d+)-комн\.', title)
    if match:
        return int(match.group(1))
    else:
        return None

def extract_and_unify_share_numeric(title):
    title = title.lower()
    match_fraction = re.search(r'(\d+)/(\d+)', title)
    if match_fraction:
        numerator = int(match_fraction.group(1))
        denominator = int(match_fraction.group(2))
        return numerator / denominator
    match_percent = re.search(r'(\d+(\.\d+)?)%', title)
    if match_percent:
        return float(match_percent.group(1)) / 100
    return 1.0

# Приведение к нижнему регистру
df['title_lower'] = df['title'].str.lower()

# Признаки для различных типов недвижимости
df['is_multicompartment'] = df['title_lower'].apply(lambda x: 1 if 'многокомнат' in x or 'апартамент' in x else 0)
df['is_studio'] = df['title_lower'].apply(lambda x: 1 if 'студия' in x else 0)
df['room_count'] = df['title_lower'].apply(extract_room_count)

# Обработка специальных случаев
df['share'] = df['title'].apply(extract_and_unify_share_numeric)

# Удаление временного столбца
df.drop(columns=['title_lower'], inplace=True)

# Функция для замены NaN на "Агентство недвижимости"
def replace_nan_with_agency(seller_type):
    if pd.isna(seller_type):
        return 'Агентство недвижимости'
    return seller_type

# Функция для замены "ID" на "Собственник"
def replace_id_with_owner(seller_type):
    if isinstance(seller_type, str) and 'id' in seller_type.lower():
        return 'Собственник'
    return seller_type

# Функция для проверки, является ли строка русским именем и фамилией
def is_russian_name_and_surname(seller_type):
    if isinstance(seller_type, str):
        seller_type_lower = seller_type.lower()
        try:
            parsed_name = russiannames.get_gender(seller_type_lower)
            if parsed_name:
                return True
        except:
            pass
    return False

# Функция для проверки, является ли строка латинским именем и фамилией
def is_latin_name_and_surname(seller_type):
    if isinstance(seller_type, str):
        seller_type_lower = seller_type.lower()
        try:
            parsed_name = HumanName(seller_type_lower)
            if parsed_name.first and parsed_name.last:
                return True
        except:
            pass
    return False

# Функция для замены имен и фамилий на "Собственник"
def replace_name_with_owner(seller_type):
    if is_russian_name_and_surname(seller_type) or is_latin_name_and_surname(seller_type):
        return 'Собственник'
    return seller_type

# Применение функций к столбцу
df['seller_type'] = df['seller_type'].apply(replace_nan_with_agency)
df['seller_type'] = df['seller_type'].apply(replace_id_with_owner)
df['seller_type'] = df['seller_type'].apply(replace_name_with_owner)

# Замена всех значений, кроме "Собственник", "Застройщик" и "Циан" на "Застройщик"
df['seller_type'] = df['seller_type'].apply(lambda x: x if x in ['Собственник', 'Застройщик', 'Циан'] else 'Застройщик')

# Список административных округов ЗелАО
moscow_districts = [
    'ЦАО', 'САО', 'СВАО', 'ВАО', 'ЮВАО', 'ЮАО', 'ЮЗАО', 'ЗАО', 'СЗАО', 'ЗелАО', 'НАО', 'ТАО'
]

# Замена NaN значений на пустую строку
df['address'] = df['address'].fillna('')

# Преобразование каждой строки в список, разделяя по запятой
df['address_list'] = df['address'].apply(lambda x: x.split(','))

# Инициализация столбцов "улица", "район" и "поселение"
df['улица'] = np.nan
df['район'] = np.nan
df['поселение'] = np.nan

# Функция для извлечения улицы, района и поселения из списка адресов
def extract_street_district_settlement(address_list):
    street = np.nan
    district = np.nan
    settlement = np.nan
    
    for part in address_list:
        part_clean = part.strip()
        if 'ул' in part_clean.lower() or 'улица' in part_clean.lower():
            street = part_clean
        elif any(district in part_clean for district in moscow_districts):
            district = part_clean
        elif 'поселение' in part_clean.lower():
            settlement = part_clean
    return street, district, settlement

# Применение функции к каждому списку и заполнение новых столбцов
df[['улица', 'район', 'поселение']] = df['address_list'].apply(lambda x: pd.Series(extract_street_district_settlement(x)))

df.loc[df['район'].isna() & df['поселение'].notna(), 'район'] = 'НАО'

df = df[df['район'].isna()==False]

df['район'] = df['район'].replace({'ТАО (Троицкий)': 'ТАО', 'НАО (Новомосковский)': 'НАО'})

df[['floor', 'total_floors']] = df['floor'].str.split(' из ', expand=True)

# Функция для очистки и преобразования значений
def clean_ceiling_height(height):
    if pd.isna(height):
        return np.nan
    try:
        # Удаление неразрывного пробела и преобразование в число
        height = height.replace('\xa0м', '').replace(',', '.')
        height = float(height)
        # Исключение аномальных значений
        return height
    except:
        return np.nan

# Применение функции к колонке 'ceiling_height'
df['ceiling_height'] = df['ceiling_height'].apply(clean_ceiling_height)


# Функция для очистки и преобразования значений площади и высоты потолков
def clean_area(value):
    try:
        return float(value.replace('\xa0', '').replace(',', '.'))
    except:
        return np.nan

# Функция для преобразования года строительства
def clean_year(value):
    try:
        year = int(value)
        if year < 1000 or year > pd.Timestamp.now().year:
            return np.nan
        return year
    except:
        return np.nan

# Преобразование данных
df['total_area'] = df['total_area'].apply(clean_area)
df['kitchen_area'] = df['kitchen_area'].apply(clean_area)

# Замена типа данных на float
df['total_area'] = df['total_area'].astype(float)
df['kitchen_area'] = df['kitchen_area'].astype(float)

# Преобразование года строительства
df['construction_year'] = df['construction_year'].apply(clean_year)

# Замена типа данных на int для construction_year
df['construction_year'] = df['construction_year'].astype('Int64')

def replace_room_count(row):
    if pd.isna(row['room_count']):
        if 0 <= row['total_area'] <= 50:
            return np.random.choice([1, 2])
        elif 50 < row['total_area'] <= 100:
            return np.random.choice([2, 3])
        elif 100 < row['total_area'] <= 150:
            return np.random.choice([3, 4])
        elif 150 < row['total_area'] <= 250:
            return np.random.choice([4, 5])
        elif row['total_area'] > 250:
            return np.random.choice([4, 5, 6, 7, 8])
    return row['room_count']

# Apply the function to the dataframe
df['room_count'] = df.apply(replace_room_count, axis=1)


# Преобразование других колонок в float
cols_to_float = ['floor', 'room_count', 'total_floors']
for col in cols_to_float:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['price_per_meter'] = df.apply(lambda row: row['price'] / row['total_area'] if pd.isna(row['price_per_meter']) and row['total_area'] != 0 else row['price_per_meter'], axis=1)


df['kitchen_area'].fillna(df['kitchen_area'].median(), inplace=True)
df['ceiling_height'].fillna(df['ceiling_height'].median(), inplace=True)

modes = df[df['renovation'].notna()].groupby('housing_type')['renovation'].agg(lambda x: x.mode()[0] if not x.mode().empty else None).to_dict()
def fill_renovation(row):
    if pd.isna(row['renovation']):
        if "Новостройка" in row['housing_type'] or "Апартаменты" in row['housing_type']:
            return "Без ремонта"
        else:
            return modes.get(row['housing_type'], "Без ремонта")
    return row['renovation']

df['renovation'] = df.apply(fill_renovation, axis=1)

# Подсчет моды и медианы
construction_year_mode = df['construction_year'].mode()[0]
construction_year_median = df['construction_year'].median()

# Списки годов для замены
new_building_years = [2021, 2022, 2023, 2024]

# Функция для замены значений
def fill_construction_year(row, new_building_years):
    if pd.isna(row['construction_year']):
        if "Новостройка" in row['housing_type']:
            return new_building_years.pop(0) if new_building_years else np.nan
        else:
            return construction_year_median
    return row['construction_year']

# Применение функции к DataFrame
df['construction_year'] = df.apply(lambda row: fill_construction_year(row, new_building_years.copy()), axis=1)

df['kitchen_ratio'] = df['kitchen_area'] / df['total_area']
df['is_new_building'] = df['housing_type'].apply(lambda x: 1 if x == 'Новостройка' else 0)

# Преобразование категориальных признаков
df = pd.get_dummies(df, columns=['housing_type', 'renovation', 'seller_type', 'район'], drop_first=True, dtype=int)

df_final = df[['price', 'price_per_meter', 'housing_type_Вторичка Апартаменты',
       'housing_type_Вторичка Пентхаус', 'housing_type_Новостройка',
       'housing_type_Новостройка Апартаменты',
       'housing_type_Новостройка Пентхаус',
       'total_area', 'kitchen_area', 'ceiling_height', 'construction_year',
       'floor', 'is_multicompartment', 'is_studio', 'share', 'room_count', 'total_floors', 'kitchen_ratio',
       'is_new_building', 'renovation_Дизайнерский', 'renovation_Евроремонт',
       'renovation_Косметический', 'seller_type_Собственник',
       'seller_type_Циан', 'район_ЗАО', 'район_ЗелАО', 'район_НАО',
       'район_САО', 'район_СВАО', 'район_СЗАО', 'район_ТАО', 'район_ЦАО',
       'район_ЮАО', 'район_ЮВАО', 'район_ЮЗАО']]


df_final.to_csv('data_processing.csv', index=False)
