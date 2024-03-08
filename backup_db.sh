#!/bin/bash

# Установите переменные для подключения к вашей базе данных
DB_NAME="SocioConnection"
DB_USER="postgres"  # Имя пользователя базы данных
DB_PASSWORD="3454325"  # Пароль для доступа к базе данных
BACKUP_DIR="backup"  # Путь к директории для сохранения бэкапов

# Текущая дата для имени файла бэкапа
CURRENT_DATE=$(date +%Y.%m.%d_%H:%M)

# Файл бэкапа
BACKUP_FILE="$BACKUP_DIR/$DB_NAME-$CURRENT_DATE.sql"

# Экспорт переменной с паролем для автоматического ввода пароля при подключении к базе данных
export PGPASSWORD=$DB_PASSWORD

# Создание бэкапа
pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_FILE

# Сброс экспортированной переменной
unset PGPASSWORD

# Вывод сообщения об успешном создании бэкапа
echo "Backup created successfully: $BACKUP_FILE"
