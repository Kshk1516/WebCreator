#!/bin/bash
# Обновляем pip и устанавливаем зависимости из requirements.txt
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Запускаем сервер
python3 index.py