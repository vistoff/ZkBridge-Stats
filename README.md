# ZkBridge-Stats
Скрипт завантажуе базу з https://dune.com/catyrn/polyhedra-zkbridge-stats

Бази данних оновлюються кожні 6 годин

Додати адресси `files/wallets.txt`

Запуск на MAC:

```
python3 -m venv env

. ./env/bin/activate

pip install -U pip

pip install -r requirements.txt

python3 main.py
```