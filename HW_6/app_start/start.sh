есhо "ожидаем базы данных"

until python -c "import os, psycopg2; psycopg.connect(os.getenv('DATABASE_URL'))" 2>/dev/null; do
  echo "База недоступна ... "
  sleep 2
done

echo "Применяем миграции"
alembic upgrade head

есho "Запускаем приложение"
python app.py
I