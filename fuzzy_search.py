import json
import os
import math
from rapidfuzz import fuzz, process

# Настройки
SCORE_CUTOFF = 60
MAX_RESULTS = 3
SHOW_DICTIONARY_FILE = "show_dictionary.json"

# Загрузка словаря
with open(SHOW_DICTIONARY_FILE, 'r', encoding='utf-8') as f:
    show_data = json.load(f)

# Создаём плоский список: (название, tconst, is_main, votes)
search_pool = []
for tconst, info in show_data.items():
    titles = info.get("titles", [])
    main_title = info.get("main")
    votes = info.get("votes", 0)
    for title in titles:
        is_main = (title == main_title)
        search_pool.append((title, tconst, is_main, votes))

def score_with_bonus(score, is_main, votes):
    bonus = 10 if is_main else 0
    vote_bonus = math.log10(votes + 1) * 2 if votes > 0 else 0
    return score + bonus + vote_bonus

def search(query):
    results = []
    query_lc = query.lower()
    for title, tconst, is_main, votes in search_pool:
        score = fuzz.token_sort_ratio(query_lc, title.lower())  # 🟢 Сравнение в нижнем регистре
        if score >= SCORE_CUTOFF:
            adjusted = score_with_bonus(score, is_main, votes)
            results.append((adjusted, score, title, tconst, votes, is_main))

    results.sort(reverse=True)
    return results[:MAX_RESULTS]

def interactive():
    while True:
        query = input("🔍 Введите название (или пусто для выхода): ").strip()
        if not query:
            break
        matches = search(query)
        if not matches:
            print("❌ Ничего не найдено.")
            continue

        print("✅ Найдено:")
        for adj_score, score, title, tconst, votes, is_main in matches:
            star = "⭐" if is_main else ""
            print(f"[{score:.0f}%] {title} → {show_data[tconst]['main']} ({tconst})  [⭐ {votes}]{' ' + star if star else ''}")

if __name__ == "__main__":
    interactive()
