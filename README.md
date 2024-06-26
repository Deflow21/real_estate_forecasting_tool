# Инструмент прогнозирования стоимости недвижимости
Инструмент прогнозирования стоимости недвижимости на основе данных с сайтов объявлений

## Обзор
Инструмент направлен на разработку инструмента для прогнозирования стоимости жилой недвижимости как актива для инвестиций частных лиц. Инструмент использует модели машинного обучения для краткосрочного прогноза цен на недвижимость на основе актуальных данных.


## На текущий момент завершены следующие этапы:

 - Сбор данных с сайта ЦИАН.
 - Предварительная обработка данных.
 - Разведывательный анализ данных.
 - Реализация и тестирование моделей машинного обучения.

## Следующие шаги
 - Интеграция с дополнительными источниками данных (Авито, Домклик, Яндекс).
 - Оптимизация моделей с использованием методов подбора гиперпараметров.
 - Разработка пользовательского интерфейса для удобного взаимодействия с системой.
 - Введение новых признаков на основе дополнительных факторов (демографические данные, инфраструктурные проекты и т.д.).
 - Автоматизация процесса обновления данных и моделей.

## Особенности
- Сбор и предварительная обработка данных с сайтов объявлений недвижимости (На данный момент только с ЦИАН).
- Анализ данных и создание новых признаков.
- Реализация различных моделей машинного обучения: линейная регрессия, случайный лес, градиентный бустинг, метод k-ближайших соседей (k-NN), метод опорных векторов (SVM).
- Оценка моделей с использованием метрик: MSE, MAE, RMSE, R² и Adjusted R².


 Обработка и прогнозирование данных о недвижимости


## Предварительные условия

- Python 3.6 или выше

## Установка

1. Клонируйте репозиторий на ваш локальный компьютер:

   git clone https://github.com/Deflow21/real_estate_forecasting_tool
   
   cd real_estate_forecasting_tool
    

3. Установите необходимые зависимости:
    
    pip install -r requirements.txt
    

## Использование

Для запуска всего процесса обработки данных выполните скрипт main.py:

python main.py

## Результаты и выводы

После выполнения main.py будут сгенерированы следующие файлы: 

| **Файл**                       | **Описание**                                                    |
|-------------------------------|-----------------------------------------------------------------|
| `listings.json`               | Содержит исходные спарсенные данные, которые были получены из различных источников. |
| `data.csv`                    | Содержит собранные данные с дополнительной информацией, которая была добавлена на этапе предварительной обработки. |
| `data_processing.csv`         | Содержит обработанные и очищенные данные, готовые для дальнейшего анализа и моделирования. |
| `model_performance_metrics.xlsx` | Содержит метрики производительности различных моделей, используемых в проекте, включая точность, полноту, F1-меру и другие показатели. |

Также происходит вывод прогноза диапозона цен на квартиры в завимости от количсества комнат в них. Прогноз на месяц вперед.
