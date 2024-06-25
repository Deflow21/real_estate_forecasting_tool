import subprocess

# Запуск скрипта data_parsing.py
print("Запуск скрипта data_parsing.py...")
subprocess.run(["python", "data_parsing.py"])

# Запуск скрипта data_collection.py
print("Запуск скрипта data_collection.py...")
subprocess.run(["python", "data_collection.py"])

# Запуск скрипта data_processing.py
print("Запуск скрипта data_processing.py...")
subprocess.run(["python", "data_processing.py"])

# Запуск скрипта data_analytics.py
print("Запуск скрипта data_analytics.py...")
subprocess.run(["python", "data_analytics.py"])

# Запуск скрипта forecast_main.py из папки data_forecasting
print("Запуск скрипта forecast_main.py из папки data_forecasting...")
subprocess.run(["python", "data_forecasting/forecast_main.py"])

print("Все скрипты успешно выполнены.")
