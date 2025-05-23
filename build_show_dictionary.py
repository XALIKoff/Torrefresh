import os
import json
import gzip
import urllib.request
from tqdm import tqdm
from collections import defaultdict

# IMDb dataset URLs
FILES = {
    "title.basics.tsv.gz": "https://datasets.imdbws.com/title.basics.tsv.gz",
    "title.akas.tsv.gz": "https://datasets.imdbws.com/title.akas.tsv.gz",
    "title.ratings.tsv.gz": "https://datasets.imdbws.com/title.ratings.tsv.gz",
}

OUTPUT_JSON = "show_dictionary.json"

# Progress bar class for downloading
class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize:
            self.total = tsize
        self.update(b * bsize - self.n)

# Download with progress
def download_with_progress(url, output_path):
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=os.path.basename(output_path)) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)

def main():
    script_dir = os.path.abspath(os.path.dirname(__file__))
    paths = {fname: os.path.join(script_dir, fname) for fname in FILES}

    # Step 1: Download files if not exist
    for fname, url in FILES.items():
        if not os.path.exists(paths[fname]):
            print(f"Скачивается {fname}...")
            download_with_progress(url, paths[fname])
        else:
            print(f"Файл {fname} уже существует — пропускаем загрузку.")

    # Step 2: Parse title.basics.tsv.gz to get valid TV shows
    valid_shows = {}
    with gzip.open(paths["title.basics.tsv.gz"], 'rt', encoding='utf-8') as f:
        header = next(f)
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3 and parts[1] in ("tvSeries", "tvMiniSeries"):
                tconst = parts[0]
                primary_title = parts[2]
                valid_shows[tconst] = {"titles": set(), "main": primary_title}

    # Step 3: Parse title.akas.tsv.gz to add alternate titles
    with gzip.open(paths["title.akas.tsv.gz"], 'rt', encoding='utf-8') as f:
        header = next(f)
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                tconst = parts[0]
                title = parts[2]
                if tconst in valid_shows and title != r"\N":
                    valid_shows[tconst]["titles"].add(title.strip())

    # Step 4: Parse title.ratings.tsv.gz to get number of votes
    ratings = {}
    with gzip.open(paths["title.ratings.tsv.gz"], 'rt', encoding='utf-8') as f:
        header = next(f)
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                tconst = parts[0]
                try:
                    votes = int(parts[2])
                    ratings[tconst] = votes
                except ValueError:
                    continue

    # Step 5: Merge ratings into valid_shows
    for tconst, data in valid_shows.items():
        data["titles"].add(data["main"])  # ensure main is included in titles
        data["titles"] = list(sorted(data["titles"]))
        data["votes"] = ratings.get(tconst, 0)

    # Step 6: Save final JSON
    output_path = os.path.join(script_dir, OUTPUT_JSON)
    with open(output_path, 'w', encoding='utf-8') as out_file:
        json.dump(valid_shows, out_file, ensure_ascii=False, indent=2)

    print(f"\nСловарь сериалов сохранён в '{OUTPUT_JSON}'")

    # Step 7: Ask whether to delete .gz files
    while True:
        choice = input("Удалить скачанные .gz файлы? (y/n): ").strip().lower()
        if choice in ("y", "yes"):
            for path in paths.values():
                os.remove(path)
            print("Файлы удалены.")
            break
        elif choice in ("n", "no"):
            print("Файлы сохранены.")
            break
        else:
            print("Введите 'y' или 'n'.")

if __name__ == "__main__":
    main()
