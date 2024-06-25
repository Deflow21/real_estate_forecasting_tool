import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Загрузка данных из CSV
df_final = pd.read_csv('data_processing.csv')

# Вывод описательной статистики
print(df_final.describe())

# Фильтрация данных для построения графиков (например, удаление выбросов)
df_filtered = df_final[df_final['price'] < df_final['price'].quantile(0.99)]

# Настройка графиков
fig, axs = plt.subplots(3, 3, figsize=(20, 15))

# Настройка цветовой палитры
palette = sns.color_palette("husl", 9)

# Гистограмма
sns.histplot(df_filtered['price'], kde=True, bins=30, ax=axs[0, 0], color=palette[0])
axs[0, 0].set_title('Гистограмма цены')
axs[0, 0].set_xlabel('Цена')
axs[0, 0].set_ylabel('Количество')

# Диаграмма размаха
sns.boxplot(y=df_filtered['price'], linewidth=2.5, ax=axs[0, 1], color=palette[1])
axs[0, 1].set_title('Диаграмма размаха цены')
axs[0, 1].set_ylabel('Цена')

# График плотности
sns.kdeplot(df_filtered['price'], linewidth=2.5, ax=axs[0, 2], color=palette[2])
axs[0, 2].set_title('График плотности цены')
axs[0, 2].set_xlabel('Цена')
axs[0, 2].set_ylabel('Плотность')

# Кумулятивная гистограмма
sns.histplot(df_filtered['price'], kde=True, bins=30, cumulative=True, ax=axs[1, 0], color=palette[3])
axs[1, 0].set_title('Кумулятивная гистограмма цены')
axs[1, 0].set_xlabel('Цена')
axs[1, 0].set_ylabel('Кумулятивное количество')

# Виолончельный график
sns.violinplot(y=df_filtered['price'], linewidth=2.5, ax=axs[1, 1], color=palette[4])
axs[1, 1].set_title('Виолончельный график цены')
axs[1, 1].set_ylabel('Цена')

# График ящиков с усами и полосами
sns.boxenplot(y=df_filtered['price'], linewidth=2.5, ax=axs[1, 2], color=palette[5])
axs[1, 2].set_title('График ящиков с усами и полосами цены')
axs[1, 2].set_ylabel('Цена')

# График распределения с полосами
sns.stripplot(y=df_filtered['price'], size=5, ax=axs[2, 0], color=palette[6])
axs[2, 0].set_title('График распределения с полосами цены')
axs[2, 0].set_ylabel('Цена')

# График эмпирической функции распределения
sns.ecdfplot(df_filtered['price'], linewidth=2.5, ax=axs[2, 1], color=palette[7])
axs[2, 1].set_title('График эмпирической функции распределения цены')
axs[2, 1].set_xlabel('Цена')
axs[2, 1].set_ylabel('Эмпирическая функция распределения')

# График рассеяния (Scatter Plot) для цены
sns.scatterplot(x=range(len(df_filtered)), y='price', data=df_filtered, ax=axs[2, 2], color=palette[8])
axs[2, 2].set_title('График рассеяния цены')
axs[2, 2].set_xlabel('Индекс')
axs[2, 2].set_ylabel('Цена')

plt.tight_layout()
plt.show()
