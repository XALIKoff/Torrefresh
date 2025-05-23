import re
import json
import requests
from qbittorrentapi import Client
from datetime import datetime, timezone
from dateutil import parser
from fuzzy_search import search as fuzzy_search_titles

# ==== Загрузка конфигов ====
with open("config.json", encoding="utf-8") as f:
    CONFIG = json.load(f)

with open("trackers.json", encoding="utf-8") as f:
    TRACKERS = json.load(f)

QBIT_HOST = CONFIG["qbit_host"]
JACKETT_API_KEY = CONFIG["jackett_api_key"]
JACKETT_HOST = CONFIG["jackett_host"]
CATEGORIES = [c.strip() for c in CONFIG.get("torrent_category", "Series").split(",")]

# ==== Telegram уведомления ====
TELEGRAM_ENABLED = CONFIG.get("telegram_enabled", False)
TELEGRAM_TOKEN = CONFIG.get("telegram_token")
TELEGRAM_CHAT_ID = CONFIG.get("telegram_chat_id")

def send_telegram_message(message):
    if not TELEGRAM_ENABLED:
        return
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"⚠ Ошибка отправки в Telegram: {e}")

# ==== Утилиты ====
def normalize_name(name):
    name = re.sub(r'\[.*?\]', '', name)
    name = name.replace('.', ' ')
    name = re.sub(r'\s+', ' ', name)
    split_patterns = [
        r'\bS\d{1,2}E\d{1,2}\b', r'\bS\d{1,2}\b', r'\bSeason\b', r'\b\d{3,4}p\b',
        r'\bWEB[- ]?DL\b', r'\bHDR\b', r'\bx?264\b', r'\bx?265\b', r'\bBluRay\b',
        r'\bRip\b', r'\bHD\b', r'\bRUSSIAN\b', r'\bRus\b'
    ]
    for pattern in split_patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            name = name[:match.start()]
            break
    return re.sub(r'[^\w\s]', '', name).strip()

def convert_to_datetime(timestamp):
    try:
        if isinstance(timestamp, (int, float)):
            return datetime.utcfromtimestamp(timestamp)
        elif isinstance(timestamp, str):
            return parser.isoparse(timestamp).astimezone().astimezone(timezone.utc).replace(tzinfo=None)
    except Exception:
        return datetime.min

def extract_id(url, regex):
    match = re.search(regex, url)
    return match.group(1) if match else None

def extract_episode_info(name, pattern):
    match = re.search(pattern, name)
    return match.groupdict() if match else None

def detect_indexer_from_url(url):
    url = url.lower()
    for key in TRACKERS:
        if key.lower() in url:
            return key
    return None

def torrent_already_exists(torrents, candidate_info, quality_levels, episode_pattern):
    for t in torrents:
        t_info = extract_episode_info(t['name'], episode_pattern)
        if not t_info:
            continue
        if (t_info.get("series") == candidate_info.get("series") and
            int(t_info.get("season", -1)) == int(candidate_info.get("season", -1)) and
            int(t_info.get("episode", -1)) == int(candidate_info.get("episode", -1))):
            if quality_levels:
                if any(q in t['name'] and q in candidate_info.get('quality', '') for q in quality_levels):
                    return True
            else:
                return True
    return False

def download_torrent_file(url, print_fn=print):
    try:
        print_fn(f"  💾 Скачиваем .torrent файл")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, allow_redirects=True, timeout=15)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print_fn(f"  ❌ Ошибка скачивания .torrent файла: {e}")
        return None

def add_torrent_to_qb(qb, torrent_content, category, save_path=None, label=None, paused=False, print_fn=print):
    try:
        qb.torrents_add(
            torrent_files=torrent_content,
            category=category,
            save_path=save_path,
            label=label,
            paused=paused
        )
        print_fn("  ✅ Торрент успешно добавлен в qBittorrent")
        return True
    except Exception as e:
        print_fn(f"  ❌ Ошибка добавления торрента в qBittorrent: {e}")
        return False

def download_and_add_torrent(qb, torrent_url, old_torrent_hash=None, preserve_files=False, category=None, print_fn=print):
    torrent_content = download_torrent_file(torrent_url, print_fn)
    if torrent_content is None:
        return False
    added = add_torrent_to_qb(qb, torrent_content, category=category, print_fn=print_fn)
    if added and old_torrent_hash and not preserve_files:
        try:
            print_fn(f"  🗑 Удаляем старый торрент (с сохранением файлов)")
            qb.torrents_delete(delete_files=False, torrent_hashes=old_torrent_hash)
        except Exception as e:
            print_fn(f"  ❌ Ошибка удаления старого торрента: {e}")
    return added

def search_and_process_results(results, method, cfg, torrents, current_info, pattern, name, comment, size_qbit, hash_qbit, added_on, category, qb, print_fn):
    found_match = False
    quality_levels = cfg["match"].get("quality_levels", [])

    for r in results:
        title = r.get('Title')
        detail_link = r.get('Details')
        torrent_link = r.get('Link')
        pub_date = r.get('PublishDate')
        size_new = r.get('Size')
        if not detail_link or not pub_date or not size_new:
            continue

        if method == "next_episode":
            candidate_info = extract_episode_info(title, pattern)
            if current_info and candidate_info:
                if (current_info["series"] == candidate_info["series"] and
                    int(candidate_info["season"]) == int(current_info["season"]) and
                    int(candidate_info["episode"]) == int(current_info["episode"]) + 1):
                    for q in quality_levels:
                        if q in name and q not in title:
                            break
                    else:
                        if torrent_already_exists(torrents, candidate_info, quality_levels, pattern):
                            print_fn(f"  ⚠ Уже добавлен S{candidate_info['season']}E{candidate_info['episode']}\n")
                            continue
                        print_fn(f'  🎯 Найдена следующая серия: {title}')
                        print_fn("")
                        download_and_add_torrent(qb, torrent_link, preserve_files=True, category=category, print_fn=print_fn)
                        send_telegram_message(f"📺 Новая серия: {title}")
                        found_match = True
                        break

        elif method == "exact_url":
            if comment.strip() == detail_link.strip():
                found_match = True
                print_fn(f'  ✅ Совпадение по ссылке')
        elif method == "compare_id":
            id_regex = cfg["match"].get("id_regex")
            id_comment = extract_id(comment, id_regex)
            id_detail = extract_id(detail_link, id_regex)
            if id_comment and id_detail and id_comment == id_detail:
                found_match = True
                print_fn(f'  🔁 Совпадение по ID: {id_comment}')

        if found_match and method in ("exact_url", "compare_id"):
            dt_added = convert_to_datetime(added_on)
            dt_publish = convert_to_datetime(pub_date)
            print_fn(f'    📅 Добавлен: {dt_added}, опубликован: {dt_publish}')
            if dt_publish > dt_added and size_new > size_qbit + 10 * 1024 * 1024:
                print_fn(f'  🔄 Обновление: +{(size_new - size_qbit)/(1024*1024):.1f} MB')
                download_and_add_torrent(qb, torrent_link, old_torrent_hash=hash_qbit, preserve_files=False, category=category, print_fn=print_fn)
                send_telegram_message(f"📦 Обновлён торрент: {name}")
            else:
                print_fn(f'  🔁 Обновлений нет\n')
            break

    return found_match

# ==== Основная функция ====
def run_update_logic(print_fn=print):
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    print_fn(f"\n🚀 Запуск скрипта — {now}")
    print_fn("🔌 Подключение к qBittorrent...")

    qb = Client(QBIT_HOST)
    try:
        qb.auth_log_in()
    except Exception as e:
        print_fn(f"❌ Ошибка подключения к qBittorrent: {e}")
        return

    torrents = qb.torrents_info()
    print_fn(f'🔍 Найдено торрентов: {len(torrents)}\n')

    for torrent in torrents:
        name = torrent['name']
        comment = torrent['comment']
        category = torrent['category']
        added_on = torrent['added_on']
        size_qbit = torrent['size']
        hash_qbit = torrent['hash']

        indexer = detect_indexer_from_url(comment if comment else name)
        if not indexer or indexer not in TRACKERS or not TRACKERS[indexer].get("enabled"):
            continue

        cfg = TRACKERS[indexer]

        if category not in CATEGORIES:
            continue

        if cfg.get("require_comment", True) and not comment:
            continue
        if cfg.get("skip_if_no_http", True) and ("http" not in comment if comment else True):
            continue

        print_fn(f'📺 {name}')
        method = cfg["match"]["method"]
        search_query = normalize_name(name)
        print_fn(f'➡ Поиск: "{search_query}" через {indexer}')

        url = f'{JACKETT_HOST}/api/v2.0/indexers/{cfg["jackett_id"]}/results'
        params = {'apikey': JACKETT_API_KEY, 'Query': search_query}

        try:
            response = requests.get(url, params=params)
            results = response.json().get('Results', [])
        except Exception as e:
            print_fn(f'  ⚠ Ошибка запроса к {indexer}: {e}')
            continue

        pattern = cfg["match"].get("episode_regex")
        current_info = extract_episode_info(name, pattern) if pattern else None

        found_match = search_and_process_results(results, method, cfg, torrents, current_info,
                                                 pattern, name, comment, size_qbit,
                                                 hash_qbit, added_on, category, qb, print_fn)

        if not found_match and method in ("compare_id", "exact_url", "next_episode"):
            # Повторный fuzzy-поиск
            print_fn("  🔎 Повторный fuzzy-поиск...")
            fuzzy_name = normalize_name(name)

            try:
                from fuzzy_search import search as fuzzy_search_titles
                from fuzzy_search import show_data
                matches = fuzzy_search_titles(fuzzy_name)
            except Exception as e:
                print_fn(f"  ⚠ Ошибка fuzzy-поиска: {e}")
                continue

            if matches:
                best_match = matches[0]
                tconst = best_match[3]
                new_query = show_data.get(tconst, {}).get("main", best_match[2])
                print_fn(f'  🔁 Пробуем альтернативный запрос: "{new_query}"')

                params['Query'] = new_query
                try:
                    response = requests.get(url, params=params)
                    results = response.json().get('Results', [])
                except Exception as e:
                    print_fn(f'  ⚠ Ошибка повторного запроса: {e}')
                    continue

                found_match = search_and_process_results(
                    results, method, cfg, torrents, current_info,
                    pattern, name, comment, size_qbit,
                    hash_qbit, added_on, category, qb, print_fn
                )

            else:
                print_fn("  ❌ Альтернативное название не найдено")



