# AIネットワーク探検室

授業「AIと社会」で使う学習用Webシステムです。AIの進展による社会の変化を，複雑ネットワーク・グラフ理論の視点から，実データのネットワークを操作しながら学びます。

**公開ページ：** https://r-shibusawa.github.io/ai-society-network/

## 収録しているネットワーク

| タブ | データ |
|---|---|
| 1 入門：SNSの友達 | SNAP ego-Facebook（McAuley & Leskovec, 2012）。1人の利用者の友達150人のつながり（匿名化済み） |
| 2 AIモデルの家系図 | Hugging Face Hub API。人気モデルの派生関係（2026年10月取得） |
| 3 AI開発組織のつながり | 同上を開発組織単位に集約 |
| 4 AIソフトウェア依存 | PyPI JSON API。主要AIライブラリ40個の依存関係（2026年10月取得） |
| 5 AI研究の国際共著 | OpenAlex。分野「人工知能」の論文（2014・2019・2024年，各5,000本の無作為抽出） |
| 6 政治ブログの分断 | Adamic & Glance (2005)。2004年アメリカ大統領選挙期の政治ブログのリンク |
| 7 うわさへの反応 | PHEME のうわさ／うわさ以外データ（Zubiaga, Liakata & Procter, 2017）を独自に集計。Twitter上の5事件における，うわさとそれ以外の投稿への返信の連鎖 |
| 8 実験室 | ランダム・スモールワールド・スケールフリーのモデル生成，推薦とエコーチェンバーのシミュレーション |

各タブで，次数・媒介中心性・PageRank などの指標の確認，ノードの削除（故障・攻撃）実験，情報・影響の広がりの実験ができます。

## 作り直す手順

```sh
python3 -m venv .venv && .venv/bin/pip install networkx scipy requests pandas
.venv/bin/python scripts/fetch_hf.py         # Hugging Face（最新にしたいときだけ）
.venv/bin/python scripts/fetch_pypi.py       # PyPI（同上）
.venv/bin/python scripts/fetch_openalex.py   # OpenAlex（同上）
scripts/fetch_sns.sh                         # Facebook・政治ブログ・PHEME
.venv/bin/python scripts/build_data.py       # ネットワーク構築・指標計算 → data/networks.json
.venv/bin/python web/build_web.py            # docs/index.html を生成
```

`docs/index.html` は外部ファイルに依存しない1枚のHTMLです（D3.js と Google Fonts のみ CDN から読み込み）。

## データの出典

- McAuley, J. & Leskovec, J. (2012). Learning to Discover Social Circles in Ego Networks. NIPS.
- Adamic, L. A. & Glance, N. (2005). The political blogosphere and the 2004 U.S. election: divided they blog. LinkKDD.
- Zubiaga, A., Liakata, M. & Procter, R. (2017). Exploiting Context for Rumour Detection in Social Media. SocInfo 2017, LNCS 10539.
- Hugging Face Hub API ／ PyPI JSON API ／ OpenAlex（Priem, J., Piwowar, H. & Orr, R., 2022）
