# Используем базовый образ Python
FROM python:3.12

# Устанавливаем рабочую директорию в контейнере
WORKDIR /hungry_shark

# Копируем зависимости в контейнер
COPY ./requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения в контейнер
COPY . .

# Команда для запуска приложения при старте контейнера
#CMD ["python", "app.py"]