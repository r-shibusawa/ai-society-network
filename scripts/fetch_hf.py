"""Hugging Face Hub から人気モデルのメタデータを取得する（ダウンロード数上位・いいね数上位）"""
import json, time, requests, sys

BASE = "https://huggingface.co/api/models"
EXPAND = ["tags", "createdAt", "author", "downloads", "likes", "pipeline_tag"]

def fetch(sort, n):
    url = BASE
    params = [("sort", sort), ("direction", "-1"), ("limit", "1000")] + [("expand[]", e) for e in EXPAND]
    out = []
    while url and len(out) < n:
        r = requests.get(url, params=params, timeout=60)
        r.raise_for_status()
        out += r.json()
        url = r.links.get("next", {}).get("url")
        params = None
        time.sleep(0.5)
        print(sort, len(out), file=sys.stderr)
    return out[:n]

models = {}
for sort, n in [("downloads", 5000), ("likes", 5000)]:
    for m in fetch(sort, n):
        models[m["id"]] = m
json.dump(list(models.values()), open("data/raw/hf_models.json", "w"))
print(len(models))
