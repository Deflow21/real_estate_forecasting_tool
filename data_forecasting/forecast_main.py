import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb

# Загрузка данных из предыдущего скрипта
df_final = pd.read_csv('data_processing.csv')

# Разделим данные на признаки и целевую переменную
X = df_final.drop(columns=['price'])
y = df_final['price']

# Функция для расчета скорректированного R-квадрата
def adjusted_r2(r2, n, k):
    return 1 - (1 - r2) * (n - 1) / (n - k - 1)

# Разделим данные на 4 равных подмножества
X_splits = np.array_split(X, 4)
y_splits = np.array_split(y, 4)

# Инициализация моделей
models = {
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(),
    'XGBoost': xgb.XGBRegressor(),
    'K-Nearest Neighbors': KNeighborsRegressor(weights='distance'),
    'Support Vector Machine': SVR(kernel='rbf')
}

# Инициализация словаря для результатов
results = []

# Обучение моделей и оценка метрик
for i, (X_subset, y_subset) in enumerate(zip(X_splits, y_splits)):
    X_train, X_test, y_train, y_test = train_test_split(X_subset, y_subset, test_size=0.2, random_state=42)
    
    for model_name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        adj_r2 = adjusted_r2(r2, len(y_test), X_test.shape[1])
        
        results.append({
            'Subset': f'Subset {i+1}',
            'Model': model_name,
            'MAE': mae,
            'MSE': mse,
            'RMSE': rmse,
            'R²': r2,
            'Adjusted R²': adj_r2      
        })

# Преобразуем результаты в DataFrame
results_df = pd.DataFrame(results)

# Преобразование результатов в необходимый табличный формат
pivot_df = results_df.pivot_table(
    index=['Model', 'Subset'],
).reset_index()

# Форматирование таблицы для отображения моделей с подмножествами и их метрик
formatted_df = pivot_df.sort_values(by=['Model', 'Subset']).set_index(['Model', 'Subset'])

# Сохранение результатов в Excel
formatted_df.to_excel("model_performance_metrics.xlsx")

# Функция для прогнозирования диапазона цен на следующий месяц
def forecast_prices(df, room_count):
    room_data = df[df['room_count'] == room_count]
    if room_data.empty:
        return f"No data for {room_count}-room apartments"
    
    mean_price = room_data['price'].mean()
    std_dev = room_data['price'].std()
    min_price = max(0, mean_price - 0.5 * std_dev)  # Уменьшаем диапазон и избегаем отрицательных значений
    max_price = mean_price + 0.5 * std_dev

    return f"Estimated price range for {room_count}-room apartments for the next month: {min_price:.2f} - {max_price:.2f}"

# Прогнозирование диапазона цен на следующий месяц для 1-6 комнатных квартир

for rooms in range(1, 7):
    print(forecast_prices(df_final, rooms))
