# 🧲 Torrefresh

Automatically update torrents in qBittorrent via Jackett.  
Supports URL and ID-based matching, episode tracking, quality preservation, and Telegram notifications.

---

## 💡 Features

- 🔍 Automatically check for updated torrents on popular trackers
- 🤖 Jackett API integration
- 📦 qBittorrent support
- 📬 Telegram notifications
- 🪪 Customizable logic per tracker (`trackers.json`)
- 🧰 GUI and CLI modes
- 🔄 Replace old torrents while keeping downloaded files

---

## 🖥 Installation & Usage

### 👉 Windows

1. Download `.exe` and `internal.zip` from [Releases](https://github.com/XALIKoff/Torrefresh/releases)
2. Extract `internal.zip` into the same folder as the `.exe`
3. Fill in `config.json`, optionally edit `trackers.json`
4. Run `Torrefresh.exe`

### 👉 Python

1. **Clone the project**
```bash
git clone https://github.com/XALIKoff/Torrefresh.git
cd Torrefresh
```

2. **Create a virtual environment and activate it**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the GUI**
```bash
python main_gui.py
```
---

## ⚙ Configuration

### `config.json`

```json
{
  "qbit_host": "http://127.0.0.1:8080/",
  "jackett_host": "http://127.0.0.1:9117",
  "jackett_api_key": "YOUR_API_KEY",
  "torrent_category": "Series",
  "telegram_enabled": true,
  "telegram_token": "YOUR_BOT_TOKEN",
  "telegram_chat_id": "YOUR_CHAT_ID"
}
```

### `trackers.json`

```json
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

---

## 📬 Telegram Notifications

1. Contact [@BotFather](https://t.me/BotFather) in Telegram
2. Send `/newbot` and follow instructions
3. Copy the token and insert it into `config.json`
4. Send any message to your bot
5. Visit:  
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`  
   to get your `chat_id`
6. Add it to `config.json`

---

## 📚 How to Use

1. Launch `main_gui.py` or the `.exe`
2. Make sure Jackett and qBittorrent are running and accessible (IP/port in `config.json`)
3. Add torrents in qBittorrent with a comment — a link to the original source
4. Click "Check updates" or set a timer for automatic checking

---

## 🛠 Dependencies

- Python 3.9+
- `qbittorrent-api`
- `requests`
- `PyQt5` (for GUI)
- `python-dateutil`

Install via:

```bash
pip install -r requirements.txt
```

---

## 🧱 Included (in internal.zip)

- `run bsd.bat` — bat, runs build_show_dictionary.py
- `build_show_dictionary.py` – script that creates series DB
- `icon.ico` – app icon

---

## 🔒 License

MIT License

---

## 🤝 Contact & Contributions

Pull requests and issues are welcome!  
[GitHub: XALIKoff/Torrefresh](https://github.com/XALIKoff/Torrefresh)

---

---

# 🇷🇺 Русская версия

## 🧲 Torrefresh

Автоматическое обновление раздач в qBittorrent через Jackett.  
Поддержка ссылочного и ID-сопоставления, отслеживание выхода новых серий, сохранение качества, уведомления в Telegram.

---

## 💡 Возможности

- 🔍 Автоматический поиск обновлений на популярных трекерах
- 🤖 Интеграция с Jackett API
- 📦 Работа с qBittorrent
- 📬 Уведомления в Telegram
- 🪪 Гибкая настройка логики через `trackers.json`
- 🧰 GUI и CLI режимы
- 🔄 Замена старой раздачи на новую с сохранением файлов

---

## 🖥 Установка и запуск

### 👉 Для Windows

1. Скачайте `.exe` и архив `internal.zip` из [Releases](https://github.com/XALIKoff/Torrefresh/releases)
2. Распакуйте `internal.zip` рядом с `.exe`
3. Настройте `config.json`, при необходимости отредактируйте `trackers.json`
4. Запустите `Torrefresh.exe`

### 👉 Для Python
1. **Клонируйте проект**
    ```bash
    git clone https://github.com/XALIKoff/Torrefresh.git
    cd Torrefresh
    ```

2. **Создайте виртуальное окружение и активируйте его**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Linux/macOS:
    source venv/bin/activate
    ```

3. **Установите зависимости**
    ```bash
    pip install -r requirements.txt
    ```

4. **Запустите GUI**
    ```bash
    python main_gui.py
    ```
---

## ⚙ Конфигурация

### `config.json`

```json
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

---

## 📬 Уведомления в Telegram

1. Напишите боту [@BotFather](https://t.me/BotFather)
2. Отправьте `/newbot` и следуйте инструкциям
3. Скопируйте токен и вставьте его в `config.json`
4. Напишите своему боту любое сообщение
5. Перейдите по ссылке:  
   `https://api.telegram.org/bot<ВАШ_ТОКЕН>/getUpdates`  
   и получите свой `chat_id`
6. Вставьте его в `config.json`

---

## 📚 Использование

1. Запустите `main_gui.py` или `.exe`
2. Убедитесь, что Jackett и qBittorrent работают по указанным адресам
3. Добавьте торренты с комментарием-ссылкой на источник
4. Нажмите «Проверить обновления» или включите таймер

---

## 🛠 Зависимости

- Python 3.9+
- `qbittorrent-api`
- `requests`
- `PyQt5`
- `python-dateutil`

Установка:

```bash
pip install -r requirements.txt
```

---

## 🧱 В архиве (internal.zip)

- `run bsd.bat` — bat файл, запускает build_show_dictionary.py
- `build_show_dictionary.py` — скрипт для создания БД сериалов
- `icon.ico` — иконка программы

---

## 🔒 Лицензия

MIT License

---

## 🤝 Контакты и помощь

Pull Request’ы и Issues приветствуются!  
[GitHub: XALIKoff/Torrefresh](https://github.com/XALIKoff/Torrefresh)
