import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import StackingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb
from tqdm import tqdm

# Предположим, что df_final уже загружен
# Разделим данные на признаки и целевую переменную
X = df_final.drop(columns=['price'])
y = df_final['price']

# Функция для расчета скорректированного R-квадрата
def adjusted_r2(r2, n, k):
    return 1 - (1 - r2) * (n - 1) / (n - k - 1)

# Функция для обучения модели и оценки метрик
def evaluate_model(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    adj_r2 = adjusted_r2(r2, len(y_test), X_test.shape[1])
    
    return {
        'MAE': mae,
        'MSE': mse,
        'RMSE': rmse,
        'R²': r2,
        'Adjusted R²': adj_r2
    }

# Функция для настройки и оценки модели с использованием GridSearchCV
def grid_search_cv(model, param_grid, X_train, y_train):
    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=3, scoring='neg_mean_squared_error', n_jobs=-1)
    grid_search.fit(X_train, y_train)
    return grid_search.best_estimator_

# Гиперпараметры для моделей
param_grids = {
    'Linear Regression': {},
    'Stacking Regressor': {
        'xgbregressor__n_estimators': [100],
        'xgbregressor__max_depth': [3],
        'xgbregressor__learning_rate': [0.1],
        'knn__n_neighbors': [5],
        'knn__weights': ['uniform'],
        'svr__C': [1],
        'svr__gamma': ['scale']
    }
}

# Разделим данные на 4 равных подмножества
X_splits = np.array_split(X, 4)
y_splits = np.array_split(y, 4)

# Инициализация базовых моделей
base_models = [
    ('xgbregressor', xgb.XGBRegressor()),
    ('knn', KNeighborsRegressor()),
    ('svr', SVR())
]

# Инициализация стекинг-регрессора
stacking_model = StackingRegressor(
    estimators=base_models,
    final_estimator=LinearRegression()
)

# Инициализация моделей
models = {
    'Linear Regression': LinearRegression(),
    'Stacking Regressor': stacking_model,
    'XGBoost': xgb.XGBRegressor(),
    'K-Nearest Neighbors': KNeighborsRegressor(),
    'Support Vector Machine': SVR()
}

# Инициализация словаря для результатов
results = []

# Обучение моделей и оценка метрик
for i, (X_subset, y_subset) in enumerate(zip(X_splits, y_splits)):
    X_train, X_test, y_train, y_test = train_test_split(X_subset, y_subset, test_size=0.2, random_state=42)
    
    for model_name, model in tqdm(models.items(), desc=f'Training models for Subset {i+1}'):
        if param_grids.get(model_name):  # Если есть параметры для настройки
            best_model = grid_search_cv(model, param_grids[model_name], X_train, y_train)
        else:
            best_model = model
        
        metrics = evaluate_model(best_model, X_train, X_test, y_train, y_test)
        metrics.update({
            'Subset': f'Subset {i+1}',
            'Model': model_name
        })
        
        results.append(metrics)

# Преобразуем результаты в DataFrame
results_df = pd.DataFrame(results)

# Формируем итоговую таблицу
pivot_df = results_df.pivot_table(index=['Model', 'Subset'], values=['MAE', 'MSE', 'RMSE', 'R²', 'Adjusted R²'])

# Сортировка индексов
pivot_df = pivot_df.sort_index(level=['Model', 'Subset'])

# Отображение лучших моделей для каждого подмножества данных
print("Лучшие модели для каждого подмножества данных:")
print(results_df)

# Отображение сводной таблицы метрик
print("Сводная таблица метрик:")
print(pivot_df)



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
