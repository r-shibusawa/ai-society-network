"""OpenAlex から「人工知能」分野の論文をランダム抽出し，著者所属国を取得する（2014/2019/2024年）"""
import json, time, requests, sys

CONCEPT = "C154945302"  # Artificial intelligence
out = {}
for year in [2014, 2019, 2024]:
    works = []
    for page in range(1, 26):  # 25 x 200 = 5000 本
        r = requests.get("https://api.openalex.org/works", params={
            "filter": f"concepts.id:{CONCEPT},publication_year:{year},type:article|preprint|proceedings-article",
            "sample": 5000, "seed": 42, "per-page": 200, "page": page,
            "select": "id,publication_year,authorships,cited_by_count"}, timeout=60)
        r.raise_for_status()
        res = r.json()["results"]
        for w in res:
            countries = sorted({c for a in w["authorships"] for c in (a.get("countries") or [])})
            works.append({"id": w["id"].rsplit("/", 1)[-1], "countries": countries, "cited": w["cited_by_count"]})
        print(year, page, len(works), file=sys.stderr)
        if not res: break
        time.sleep(0.3)
    out[year] = works
json.dump(out, open("data/raw/openalex_ai_countries.json", "w"))
