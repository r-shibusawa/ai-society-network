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
