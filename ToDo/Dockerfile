 # 1. Берём готовый образ: маленький Linux, в котором уже есть Python 3.12
  FROM python:3.12-slim

  # 2. Две полезные настройки Python:
  #    не создавать .pyc-файлы и сразу выводить логи (без задержки)
  ENV PYTHONDONTWRITEBYTECODE=1
  ENV PYTHONUNBUFFERED=1

  # 3. Рабочая папка внутри контейнера (как cd, только папка создаётся сама)
  WORKDIR /app

  # 4. Сначала копируем ТОЛЬКО список библиотек и ставим их
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

    # 5. Теперь копируем весь остальной код
  COPY . .

  # 6. Собираем статику (CSS/JS) прямо при сборке образа
  RUN python manage.py collectstatic --noinput

  # 7. Сообщаем, что приложение слушает порт 8000
  EXPOSE 8000

  # 8. Команда, которая выполнится при ЗАПУСКЕ контейнера:
  #    создать таблицы в базе и запустить gunicorn
  CMD ["sh", "-c", "python manage.py migrate && gunicorn ToDo.wsgi:application --bind 0.0.0.0:8000"]