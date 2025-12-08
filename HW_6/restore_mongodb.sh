# args
if [ $# -eq 0 ]; then
  echo "Использование: $0 <имя бэкапа> <имя базы>"
  echo "Пример: $0 db_backup_2025-01-01.tar.gz test_db"
  exit 0
fi

BACKUP_FILE=$1
DATABASE_NAME=$2


# временная лапка
# mkdir # mktemp
TEMP_DIR=$(mktemp -d)

# распаковка
echo "Распаковываем архив"
tar -xzf "$ARCHIVE" -C "$TEMP_DIR"

# ищем mongodb
MONGO_DIR=$(find "$TEMP_DIR" -type d -name "mongodb _* " | head -n 1)

if [ -z "$MONGO_DIR" ]; then
  echo "Не удалось найти директорию MongoDB в архиве"
  rm -rf "$TEMP_DIR"
  exit 1
fi

# восстановление
echo "Восстановление mongodb базы"
mongorestore -- host localhost -- db "$DB_NAME" "$MONGO_DIR/$DB_NAME"

rm -rf "$TEMP_DIR"

echo "Восстановление заверщено"
