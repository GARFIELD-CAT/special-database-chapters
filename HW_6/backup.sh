# SETTINGS

BACKUP_DIR="/Users/spbja/db/backups"
DATE=$(date +%Y-%m-%d)

# Папка для бэкапов
mkdir -p $BACKUP_DIR

# postgresql
echo "Бэкап PostgreSQL"

export PGPASSWORD='password'

pg_dump -h localhost -U postgres > $BACKUP_DIR/postgres_$DATE.sql

# mongodb
echo "Бэкап MongoDB"
mongodump --host localhost --out $BACKUP_DIR/mongodb_$DATE

# archive
echo "Создаем архив"
tar -caf $$BACKUP_DIR/db_backup_$DATE.tar.gz \
  $BACKUP_DIR/postgres_$DATE.sql \
  $BACKUP_DIR/mongodb_$DATE

# удаляем временное
rm -f $BACKUP_DIR/postgres_$DATE.sql
rm -fr $BACKUP_DIR/mongodb_$DATE

# удаляем старые бэкапы
find $BACKUP_DIR -name "db_backup_*.tar.gz" -mtime +7 -delete

echo "Бэкап завершен"

# crontab -e
#0 2 * * * /Users/spbja/db/backups/backup.sh
