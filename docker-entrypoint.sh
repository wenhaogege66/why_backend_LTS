#!/bin/bash

# 等待数据库就绪
echo "Waiting for database..."
while ! nc -z db 3306; do
  sleep 0.1
done
echo "Database is ready!"

# 执行数据库迁移
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# 启动开发服务器
echo "Starting development server..."
python manage.py runserver 0.0.0.0:8000 