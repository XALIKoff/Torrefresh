# 🧲 Torrefresh
Автоматическое обновление обновляемых раздач в qbittorrent через jackett.
Отслеживание изменений в раздаче по ссылке из comment, сохранение качества для трекеров где серии выкладываются отдельно, уведомления в Telegram (нужно создать бота).

# 💡 Возможности
🔍 Автоматический поиск обновления имеющихся раздач на популярных трекерах

🤖 Работа с Jackett API

📦 Интеграция с qBittorrent

📬 Уведомления в Telegram

🪪 Настройка логики для трекеров через trackers.json

🧰 GUI и CLI-режимы

📦 Автоматическое скачивание новой версии раздачи и удаление предыдущей (с сохранением файлов)

# 👉 Для Windows
Скачайте exe + zip, распакуйте zip рядом с exe.
заполните настройки в config.json, при желании настройте трекеры

# 👉 Для Python
git clone https://github.com/XALIKoff/Torrefresh.git
cd Torrefresh
pip install -r requirements.txt
python main_gui.py

# ⚙ Конфигурация
config.json:
```
{
  "qbit_host": "http://127.0.0.1:8080/",
  "jackett_host": "http://127.0.0.1:9117",
  "jackett_api_key": "ТВОЙ_АПИ_КЛЮЧ",
  "torrent_category": "Series",
  "telegram_enabled": true,
  "telegram_token": "ТОКЕН_ТВОЕГО_БОТА",
  "telegram_chat_id": "ТВОЙ_CHAT_ID"  
}
```

trackers.json:
```
{
  "rutracker": {
    "enabled": true,
    "jackett_id": "rutracker",
    "match": {
      "method": "exact_url"
    },
    "require_comment": true,
    "skip_if_no_http": true
  },
  "rudub": {
    "enabled": true,
    "jackett_id": "rudub",
    "match": {
      "method": "compare_id",
      "id_regex": "id=(\\d+)"
    },
    "require_comment": true,
    "skip_if_no_http": true
  },
  "kinozal": {
    "enabled": true,
    "jackett_id": "kinozal",
    "match": {
       "method": "exact_url"
    },
    "require_comment": true,
    "skip_if_no_http": true
  },
  "lostfilm": {
    "enabled": true,
    "jackett_id": "lostfilm",
    "match": {
      "method": "next_episode",
      "episode_regex": "(?P<series>.+?)\\.S(?P<season>\\d{1,2})E(?P<episode>\\d{1,2})(?:\\.|\\b).*?(?P<quality>\\d{3,4}p)?",
      "quality_levels": ["1080p", "720p"]
    },
    "require_comment": false,
    "skip_if_no_http": false
  }
}
```
# Настройка Telegram-бота для уведомлений
1. Напишите в Telegram боту @BotFather.
2. Отправьте /newbot и создайте своего бота.
3. Скопируйте выданный токен в config.json.
4. Напишите своему боту любое сообщение — он ответит вам.
5. Откройте этот сайт: https://api.telegram.org/bot<ВАШ_ТОКЕН>/getUpdates
   и получите свой chat_id.
6. Скопируйте свой chat_id в config.json

# 📚 Использование
Запустите GUI через main_gui.py или .exe

Убедитесь, что Jackett и qBittorrent работают и доступны локально, ip и порты нужно указать в json.

Добавьте нужные торренты в qBittorrent с комментарием — ссылкой на оригинальный источник

Нажмите кнопку «Проверить обновления» или настройте таймер

# 🛠 Зависимости
Python 3.9+
qbittorrent-api
requests
PyQt5 (для GUI)
python-dateutil

Установить можно через:

pip install -r requirements.txt

🔒 Лицензия
MIT License

🤝 Контакты и помощь
Pull request'ы и Issues приветствуются!

