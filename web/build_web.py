"""web/app_template.html に data/networks.json を埋め込み，配布用の HTML を作る

- web/dist/app.html   : Claude Artifact 用（<html>/<head> なし）
- web/dist/index.html : GitHub Pages などに置ける単体 HTML（docs/index.html にも同じものを出力）
"""
import json, pathlib

root = pathlib.Path(__file__).resolve().parent
N = json.load(open(root.parent / "data/networks.json"))
keys = ["fb", "hf_models", "hf_orgs", "pypi", "collab_2014", "collab_2019", "collab_2024", "polblogs", "pheme"]
sel = {k: N[k] for k in keys}
# スライドの図にだけ使う大きな配列は Web には載せない
sel["pheme"] = {k: v for k, v in N["pheme"].items() if k not in ("replyMinutes", "rtAll", "sizeRumor", "sizeNon")}
# 国際共著：年を切り替えても同じ国が同じ場所に来るよう，3時点を1つの配置にそろえる
# （2024年の配置を基準にし，2024年に出てこない国だけ，2019年→2014年の配置を使う）
import copy
pos = {}
for y in ["2024", "2019", "2014"]:
    for n in N[f"collab_{y}"]["nodes"]:
        pos.setdefault(n["id"], (n["x"], n["y"]))
# build_data.py の国名表にない国（論文の少ない国）は，ここで日本語名を補う
MORE_JA = {"AM": "アルメニア", "AZ": "アゼルバイジャン", "BN": "ブルネイ", "BO": "ボリビア", "BY": "ベラルーシ",
           "CD": "コンゴ民主共和国", "CI": "コートジボワール", "CM": "カメルーン", "CR": "コスタリカ", "CU": "キューバ",
           "DO": "ドミニカ共和国", "GE": "ジョージア", "GM": "ガンビア", "GY": "ガイアナ", "HT": "ハイチ", "KM": "コモロ",
           "LA": "ラオス", "LY": "リビア", "MD": "モルドバ", "MG": "マダガスカル", "MN": "モンゴル", "MR": "モーリタニア",
           "MT": "マルタ", "MW": "マラウイ", "PR": "プエルトリコ", "PS": "パレスチナ", "SD": "スーダン", "SY": "シリア",
           "TZ": "タンザニア", "UG": "ウガンダ", "UY": "ウルグアイ", "VE": "ベネズエラ", "XK": "コソボ", "YE": "イエメン",
           "ZW": "ジンバブエ"}
for y in ["2014", "2019", "2024"]:
    sel[f"collab_{y}"] = copy.deepcopy(N[f"collab_{y}"])
    for n in sel[f"collab_{y}"]["nodes"]:
        n["x"], n["y"] = pos[n["id"]]
        if n["id"] in MORE_JA:
            n["label"] = MORE_JA[n["id"]]
data = json.dumps(sel, ensure_ascii=False, separators=(",", ":"))
body = (root / "app_template.html").read_text().replace("/*__DATA__*/", data.replace("</", "<\\/"))
out = root / "dist"
out.mkdir(exist_ok=True)
(out / "app.html").write_text(body)
(out / "index.html").write_text(
    '<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    + body.replace("<style>", "<style>\n:root { color-scheme: light; }", 1).replace("<div class=\"wrap\">", "</head>\n<body>\n<div class=\"wrap\">", 1)
    + "\n</body>\n</html>\n")
(root.parent / "docs").mkdir(exist_ok=True)
(root.parent / "docs/index.html").write_text((out / "index.html").read_text())
print(len(body) // 1024, "KB")
