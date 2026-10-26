"""取得した実データからネットワークを構築し，指標を計算して Web システム用 JSON を出力する

出力: data/networks.json （web/build_web.py が HTML に埋め込む）
"""
import json, math, random, collections
import numpy as np
import networkx as nx

random.seed(0)
OUT = {}

COUNTRY_JA = {
    "US": "アメリカ", "CN": "中国", "GB": "イギリス", "DE": "ドイツ", "JP": "日本", "FR": "フランス",
    "IN": "インド", "KR": "韓国", "CA": "カナダ", "AU": "オーストラリア", "IT": "イタリア", "ES": "スペイン",
    "ID": "インドネシア", "BR": "ブラジル", "IR": "イラン", "SA": "サウジアラビア", "PK": "パキスタン",
    "TW": "台湾", "HK": "香港", "SG": "シンガポール", "NL": "オランダ", "CH": "スイス", "SE": "スウェーデン",
    "MY": "マレーシア", "TR": "トルコ", "RU": "ロシア", "PL": "ポーランド", "EG": "エジプト", "VN": "ベトナム",
    "MX": "メキシコ", "PT": "ポルトガル", "GR": "ギリシャ", "BE": "ベルギー", "AT": "オーストリア",
    "DK": "デンマーク", "FI": "フィンランド", "NO": "ノルウェー", "IE": "アイルランド", "IL": "イスラエル",
    "AE": "アラブ首長国連邦", "TH": "タイ", "BD": "バングラデシュ", "NG": "ナイジェリア", "ZA": "南アフリカ",
    "MA": "モロッコ", "DZ": "アルジェリア", "TN": "チュニジア", "IQ": "イラク", "JO": "ヨルダン",
    "QA": "カタール", "CZ": "チェコ", "RO": "ルーマニア", "HU": "ハンガリー", "UA": "ウクライナ",
    "CL": "チリ", "AR": "アルゼンチン", "CO": "コロンビア", "NZ": "ニュージーランド", "PH": "フィリピン",
    "LK": "スリランカ", "NP": "ネパール", "ET": "エチオピア", "KE": "ケニア", "GH": "ガーナ",
    "OM": "オマーン", "KW": "クウェート", "LB": "レバノン", "PE": "ペルー", "EC": "エクアドル",
    "SI": "スロベニア", "SK": "スロバキア", "RS": "セルビア", "HR": "クロアチア", "BG": "ブルガリア",
    "LT": "リトアニア", "LV": "ラトビア", "EE": "エストニア", "LU": "ルクセンブルク", "CY": "キプロス",
    "MO": "マカオ", "KZ": "カザフスタン", "UZ": "ウズベキスタン", "BH": "バーレーン", "IS": "アイスランド",
}


def metrics(G, weight=None, k_btw=None):
    """各ノードの中心性とコミュニティ，ネットワーク全体の統計量を計算する"""
    U = G.to_undirected() if G.is_directed() else G
    btw = nx.betweenness_centrality(U, k=k_btw, seed=1, normalized=True)
    pr = nx.pagerank(G, weight=weight)
    comms = nx.community.louvain_communities(U, weight=weight, seed=1, resolution=1.0)
    comms = sorted(comms, key=len, reverse=True)
    comm_of = {n: i for i, c in enumerate(comms) for n in c}
    clust = nx.clustering(U)
    giant = max(nx.connected_components(U), key=len)
    Ug = U.subgraph(giant)
    if Ug.number_of_nodes() <= 800:
        apl = nx.average_shortest_path_length(Ug)
        diam = nx.diameter(Ug)
    else:  # 大きいネットワークはサンプリングで近似
        srcs = random.sample(list(giant), 300)
        ds = [d for s in srcs for d in nx.single_source_shortest_path_length(Ug, s).values() if d > 0]
        apl, diam = sum(ds) / len(ds), max(ds)
    n, m = U.number_of_nodes(), U.number_of_edges()
    stats = {
        "nodes": n, "edges": m, "avgDegree": round(2 * m / n, 2),
        "density": round(nx.density(U), 4),
        "clustering": round(nx.average_clustering(U), 3),
        # 同じノード数・リンク数のランダムグラフのクラスター係数（比較用）
        "clusteringRandom": round(2 * m / n / max(n - 1, 1), 4),
        "avgPath": round(apl, 2), "diameter": diam,
        "components": nx.number_connected_components(U),
        "giantShare": round(len(giant) / n, 3),
        "communities": len(comms),
        "modularity": round(nx.community.modularity(U, comms, weight=weight), 3),
    }
    return btw, pr, comm_of, clust, stats


def layout(G, k=None, iters=200, weight=None, seed=7, kk=False):
    U = G.to_undirected() if G.is_directed() else G
    if kk:  # 中規模の連結グラフは Kamada-Kawai 法の方が見やすい
        pos = nx.kamada_kawai_layout(U)
    else:
        pos = nx.spring_layout(U, k=k, iterations=iters, seed=seed, weight=weight)
    return {n: (round(float(x), 4), round(float(y), 4)) for n, (x, y) in pos.items()}


def pack(G, pos, btw, pr, comm_of, clust, extra=None, label=None, weight=None):
    U = G.to_undirected() if G.is_directed() else G
    nodes = []
    for n in G.nodes():
        d = {
            "id": n, "label": label(n) if label else n,
            "x": pos[n][0], "y": pos[n][1],
            "deg": U.degree(n),
            "btw": round(btw[n], 5), "pr": round(pr[n], 5),
            "comm": comm_of[n], "cc": round(clust[n], 3),
        }
        if weight:
            d["strength"] = U.degree(n, weight=weight)
        if G.is_directed():
            d["in"] = G.in_degree(n)
            d["out"] = G.out_degree(n)
        if extra:
            d.update(extra(n))
        nodes.append(d)
    links = []
    for a, b, data in G.edges(data=True):
        e = {"s": a, "t": b}
        if weight:
            e["w"] = data.get(weight, 1)
        if "kind" in data:
            e["k"] = data["kind"]
        links.append(e)
    return nodes, links


# ------------------------------------------------------------------ 1. SNS の友達ネットワーク（Facebook）
# SNAP ego-Facebook のうち1人（ego 414）の「友達どうしのつながり」。本人ノードを加える
EGO = "414"
F = nx.read_edgelist(f"data/raw/fb/facebook/{EGO}.edges")
for v in list(F.nodes()):
    F.add_edge("ego", v)
circles = [l.split()[1:] for l in open(f"data/raw/fb/facebook/{EGO}.circles")]
circles = sorted(circles, key=len, reverse=True)
circle_of = {}
for i, c in enumerate(circles):  # 大きいリストから順に割り当て（重複する人は大きいリスト側）
    for v in c:
        circle_of.setdefault(v, f"分類{'ABCDEFGH'[i]}" if i < 8 else "その他の分類")
num = {v: i + 1 for i, v in enumerate(sorted((v for v in F if v != "ego"), key=int))}
F = nx.relabel_nodes(F, {v: ("人物X" if v == "ego" else f"友達{num[v]}") for v in F})
circle_of = {f"友達{num[v]}": c for v, c in circle_of.items() if v in num}
btw, pr, comm, clust, stats = metrics(F)
pos = layout(F, iters=400, k=0.12)
nodes, links = pack(F, pos, btw, pr, comm, clust,
                    extra=lambda n: {"circle": "人物X" if n == "人物X" else circle_of.get(n, "分類なし")})
OUT["fb"] = {
    "title": "SNSの友達ネットワーク（Facebook）", "directed": False,
    "source": "SNAP ego-Facebook（McAuley & Leskovec, 2012）。ある1人の利用者の友達150人と，その友達どうしのつながり（匿名化済み）",
    "edgeNote": "線＝Facebook上の友達関係。「人物X」は全員とつながっている",
    "nodes": nodes, "links": links, "stats": stats,
}

# ------------------------------------------------------------------ 2. Hugging Face モデルの派生関係
ms = json.load(open("data/raw/hf_models.json"))
meta = {m["id"]: m for m in ms}
H = nx.DiGraph()
kinds = {}
for m in ms:
    for t in m.get("tags", []):
        if t.startswith("base_model:") and t.count(":") == 2:
            _, kind, base = t.split(":", 2)
            kinds[(m["id"], base)] = kind
for m in ms:
    for t in m.get("tags", []):
        if t.startswith("base_model:") and t.count(":") == 1:
            base = t.split(":", 1)[1]
            if base != m["id"]:
                H.add_edge(m["id"], base, kind=kinds.get((m["id"], base), "finetune"))
HU = H.to_undirected()
keep = set().union(*[c for c in nx.connected_components(HU) if len(c) >= 10])
H = H.subgraph(keep).copy()
btw, pr, comm, clust, stats = metrics(H, k_btw=400)
pos = layout(H, iters=150)

def hf_extra(n):
    m = meta.get(n, {})
    return {"org": n.split("/")[0], "task": m.get("pipeline_tag") or "",
            "downloads": m.get("downloads"), "likes": m.get("likes"),
            "created": (m.get("createdAt") or "")[:10]}

nodes, links = pack(H, pos, btw, pr, comm, clust, extra=hf_extra, label=lambda n: n.split("/")[-1])
OUT["hf_models"] = {
    "title": "AIモデルの家系図（Hugging Face）", "directed": True,
    "source": "Hugging Face Hub API（ダウンロード数上位5,000件＋いいね数上位5,000件のモデルの base_model 情報，2026年10月取得）",
    "edgeNote": "矢印は「派生モデル → 元になった基盤モデル」",
    "nodes": nodes, "links": links, "stats": stats,
}

# 組織レベルに集約したネットワーク（全エッジを使用）
Hall = nx.DiGraph()
for m in ms:
    for t in m.get("tags", []):
        if t.startswith("base_model:") and t.count(":") == 1:
            Hall.add_edge(m["id"], t.split(":", 1)[1])
Org = nx.DiGraph()
for a, b in Hall.edges():
    oa, ob = a.split("/")[0], b.split("/")[0]
    if oa == ob:
        continue
    w = Org.get_edge_data(oa, ob, {"weight": 0})["weight"]
    Org.add_edge(oa, ob, weight=w + 1)
OrgU = Org.to_undirected()
keep = [n for n in Org.nodes() if Org.degree(n, weight="weight") >= 2]
Org = Org.subgraph(max(nx.connected_components(Org.subgraph(keep).to_undirected()), key=len)).copy()
btw, pr, comm, clust, stats = metrics(Org, weight="weight")
pos = layout(Org, kk=True)
nodes, links = pack(Org, pos, btw, pr, comm, clust, weight="weight",
                    extra=lambda n: {"used": Org.in_degree(n, weight="weight")})
OUT["hf_orgs"] = {
    "title": "AI開発組織のつながり（Hugging Face）", "directed": True,
    "source": "上記 Hugging Face データを開発組織（アカウント）単位に集約。重み＝派生モデル数",
    "edgeNote": "矢印は「派生モデルを作った組織 → 基盤モデルを公開した組織」",
    "nodes": nodes, "links": links, "stats": stats,
}

# 年ごとの「どの組織の基盤モデルから派生したか」（スライド用）
by_year = collections.defaultdict(collections.Counter)
for a, b in Hall.edges():
    y = (meta.get(a, {}).get("createdAt") or "")[:4]
    if y:
        by_year[y][b.split("/")[0]] += 1
OUT["hf_base_by_year"] = {y: dict(c) for y, c in sorted(by_year.items())}
OUT["hf_indegree_all"] = [d for _, d in Hall.in_degree() if d > 0]

# ------------------------------------------------------------------ 3. PyPI 依存関係
P = json.load(open("data/raw/pypi_deps.json"))
D = nx.DiGraph()
for a, v in P.items():
    D.add_node(a)
    for b in v["deps"]:
        if b in P and b != a:
            D.add_edge(a, b)
D = D.subgraph(max(nx.connected_components(D.to_undirected()), key=len)).copy()
btw, pr, comm, clust, stats = metrics(D)
pos = layout(D, kk=True)

def py_extra(n):
    # このパッケージが壊れたら影響を受けるパッケージ数（推移的に依存しているもの）
    return {"summary": P[n]["summary"], "version": P[n]["version"], "seed": P[n]["seed"],
            "affected": len(nx.ancestors(D, n))}

nodes, links = pack(D, pos, btw, pr, comm, clust, extra=py_extra)
OUT["pypi"] = {
    "title": "AIソフトウェアの依存関係（PyPI）", "directed": True,
    "source": "PyPI JSON API（主要AIライブラリ40個から必須依存を3段階たどる，2026年10月取得）",
    "edgeNote": "矢印は「利用する側 → 依存しているライブラリ」",
    "nodes": nodes, "links": links, "stats": stats,
}

# ------------------------------------------------------------------ 4. AI研究の国際共著
O = json.load(open("data/raw/openalex_ai_countries.json"))
collab_summary = {}
for year in ["2014", "2019", "2024"]:
    ws = O[year]
    C = nx.Graph()
    papers = collections.Counter()
    for w in ws:
        cs = w["countries"]
        for c in cs:
            papers[c] += 1
            C.add_node(c)
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                a, b = cs[i], cs[j]
                wgt = C.get_edge_data(a, b, {"weight": 0})["weight"]
                C.add_edge(a, b, weight=wgt + 1)
    C = C.subgraph(max(nx.connected_components(C), key=len)).copy()
    btw, pr, comm, clust, stats = metrics(C, weight="weight")
    # 向きは毎年そろえる（アメリカが左，中国が右）。Kamada-Kawai 法で配置
    p = nx.kamada_kawai_layout(C)
    if p["US"][0] > p["CN"][0]:
        p = {n: (-x, y) for n, (x, y) in p.items()}
    pos = {n: (round(float(x), 4), round(float(y), 4)) for n, (x, y) in p.items()}
    nodes, links = pack(C, pos, btw, pr, comm, clust, weight="weight",
                        label=lambda n: COUNTRY_JA.get(n, n),
                        extra=lambda n: {"papers": papers[n], "code": n})
    with_c = [w for w in ws if w["countries"]]
    intl = sum(1 for w in with_c if len(w["countries"]) > 1)
    stats["sampledPapers"] = len(ws)
    stats["papersWithCountry"] = len(with_c)
    stats["intlShare"] = round(intl / len(with_c), 3)
    OUT[f"collab_{year}"] = {
        "title": f"AI研究の国際共同研究（{year}年）", "directed": False,
        "source": f"OpenAlex（分野「人工知能」の{year}年の論文から無作為に5,000本を抽出し，著者の所属国を集計）",
        "edgeNote": "線の太さ＝共著論文数",
        "nodes": nodes, "links": links, "stats": stats,
    }
    collab_summary[year] = {
        "papers": dict(papers.most_common(15)),
        "btw": {n["id"]: n["btw"] for n in nodes},
        "deg": {n["id"]: n["deg"] for n in nodes},
        "intlShare": stats["intlShare"],
    }
OUT["collab_summary"] = collab_summary
# ------------------------------------------------------------------ 5. 政治ブログのリンク（分極化）
# 元データには重複エッジがあるので多重グラフとして読み込んでから単純グラフにする
B = nx.parse_gml(open("data/raw/polblogs/polblogs.gml").read().replace("directed 1", "directed 1\n  multigraph 1", 1), label="id")
B = nx.DiGraph(B)
B.remove_edges_from(nx.selfloop_edges(B))
B = B.subgraph(max(nx.connected_components(B.to_undirected()), key=len)).copy()
lean = {n: B.nodes[n]["value"] for n in B}
names = {n: B.nodes[n]["label"] for n in B}
B = nx.relabel_nodes(nx.DiGraph(B.edges()), names)
lean = {names[n]: v for n, v in lean.items()}
btw, pr, comm, clust, stats = metrics(B, k_btw=400)
pos = layout(B, iters=150)
cross = sum(1 for a_, b_ in B.edges() if lean[a_] != lean[b_]) / B.number_of_edges()
stats["crossShare"] = round(cross, 3)
nodes, links = pack(B, pos, btw, pr, comm, clust,
                    extra=lambda n: {"lean": "リベラル" if lean[n] == 0 else "保守"})
OUT["polblogs"] = {
    "title": "政治ブログのリンク（2004年アメリカ大統領選挙）", "directed": True,
    "source": "Adamic & Glance (2005) The political blogosphere and the 2004 U.S. election。政治ブログ1,222件のリンク",
    "edgeNote": "矢印は「リンクを張ったブログ → リンク先のブログ」",
    "nodes": nodes, "links": links, "stats": stats,
}

# ------------------------------------------------------------------ 6. Twitter のうわさ（未確認情報）の広がり方
import glob
import pandas as pd
df = pd.concat([pd.read_csv(f, low_memory=False) for f in sorted(glob.glob("data/raw/pheme/tweets_*.csv"))])
src = df[df.is_source_tweet == 1].set_index("thread")
df["t"] = (df.created - df.thread.map(src.created)) / 60000  # 元投稿からの経過分
EVENT_JA = {"charliehebdo": "シャルリー・エブド襲撃（2015）", "ferguson": "ファーガソン騒乱（2014）",
            "germanwings-crash": "ジャーマンウイングス墜落（2015）", "ottawashooting": "オタワ議会銃撃（2014）",
            "sydneysiege": "シドニー人質事件（2014）"}


def radial(T, root):
    """返信ツリーを放射状に並べる（葉の数に応じて角度を割り当てる）"""
    leaves = {}
    for v in reversed(list(nx.dfs_preorder_nodes(T, root))):
        ch = list(T.successors(v))
        leaves[v] = sum(leaves[c] for c in ch) if ch else 1
    pos = {root: (0.0, 0.0)}
    def rec(v, a0, a1, d):
        a = a0
        for c in sorted(T.successors(v), key=lambda c: -leaves[c]):
            w = (a1 - a0) * leaves[c] / leaves[v]
            th = a + w / 2
            pos[c] = (round(d * math.cos(th), 4), round(d * math.sin(th), 4))
            rec(c, a, a + w, d + 1)
            a += w
    rec(root, 0, 2 * math.pi, 1)
    return pos


cascades = []
summary = []
for th, g in df.groupby("thread"):
    s0 = src.loc[th]
    ids = {float(t): t for t in g.tweet_id}
    T = nx.DiGraph()
    T.add_node(th)
    for r in g.itertuples():
        if r.is_source_tweet == 0:
            par = ids.get(float(r.in_reply_tweet)) if not pd.isna(r.in_reply_tweet) else None
            T.add_edge(par if par in ids.values() and par != r.tweet_id else th, r.tweet_id)
    T = nx.bfs_tree(T, th)
    depth = nx.single_source_shortest_path_length(T, th)
    tmin = dict(zip(g.tweet_id, g.t))
    reps = [tmin[v] for v in T if v != th]
    summary.append({"event": s0.event, "rumor": int(s0.is_rumor), "size": T.number_of_nodes(),
                    "depth": max(depth.values()), "rt": int(s0.retweet_count),
                    "med": round(float(np.median(reps)), 1) if reps else None,
                    "verified": int(s0["user.verified"])})
    cascades.append((th, s0, T, depth, tmin))

# 表示用：各事件・うわさ／非うわさごとに大きい順に6本ずつ
pick = []
for ev in EVENT_JA:
    for rum in (1, 0):
        cs = [c for c in cascades if c[1].event == ev and int(c[1].is_rumor) == rum]
        pick += sorted(cs, key=lambda c: -c[2].number_of_nodes())[:6]
casc_out = []
for k, (th, s0, T, depth, tmin) in enumerate(pick):
    pos = radial(T, th)
    idx = {v: i for i, v in enumerate(T.nodes())}
    casc_out.append({
        "id": k, "event": s0.event, "eventJa": EVENT_JA[s0.event], "rumor": int(s0.is_rumor),
        "rt": int(s0.retweet_count), "size": T.number_of_nodes(), "depth": max(depth.values()),
        "verified": int(s0["user.verified"]),
        "nodes": [{"x": pos[v][0], "y": pos[v][1], "d": depth[v], "t": round(max(0.0, float(tmin[v])), 1)} for v in T.nodes()],
        "links": [[idx[a_], idx[b_]] for a_, b_ in T.edges()],
    })
S = pd.DataFrame(summary)
rep = df[df.is_source_tweet == 0]
OUT["pheme"] = {
    "source": "PHEME のうわさ／うわさ以外データ（Zubiaga, Liakata & Procter, 2017）をこの授業で独自に集計。Twitter 上の5つの大事件で，うわさ（未確認情報）とそれ以外の投稿への返信の連鎖。匿名化して構造と時刻のみ使用",
    "cascades": casc_out,
    "byEvent": [{"event": ev, "eventJa": EVENT_JA[ev],
                 "medRumor": round(float(rep[(rep.event == ev) & (rep.is_rumor == 1)].t.median()), 1),
                 "medNon": round(float(rep[(rep.event == ev) & (rep.is_rumor == 0)].t.median()), 1),
                 "nRumor": int((S.event == ev).mul(S.rumor == 1).sum()), "nNon": int((S.event == ev).mul(S.rumor == 0).sum())}
                for ev in EVENT_JA],
    "threads": len(S), "tweets": len(df),
    "rtTop1": round(float(np.sort(S.rt)[::-1][: len(S) // 100].sum() / S.rt.sum()), 3),
    "rtTop10": round(float(np.sort(S.rt)[::-1][: len(S) // 10].sum() / S.rt.sum()), 3),
    "within10": round(float((rep.t <= 10).mean()), 3), "within60": round(float((rep.t <= 60).mean()), 3),
    "medRumor": round(float(rep[rep.is_rumor == 1].t.median()), 1), "medNon": round(float(rep[rep.is_rumor == 0].t.median()), 1),
    "verifiedRumor": round(float(S[S.rumor == 1].verified.mean()), 3), "verifiedNon": round(float(S[S.rumor == 0].verified.mean()), 3),
    "rtAll": [int(x) for x in S.rt], "sizeRumor": [int(x) for x in S[S.rumor == 1]["size"]], "sizeNon": [int(x) for x in S[S.rumor == 0]["size"]],
    "replyMinutes": [round(float(x), 1) for x in rep.t[rep.t <= 24 * 60]],
}

# ------------------------------------------------------------------ 7. 指標の計算例（スライド用の小さなグラフ）
TG = nx.Graph([("A", "B"), ("A", "C"), ("B", "C"), ("C", "D"), ("D", "E"), ("D", "F"), ("E", "F")])
OUT["tiny"] = {
    "deg": {v: TG.degree(v) for v in TG}, "degc": {v: round(c, 3) for v, c in nx.degree_centrality(TG).items()},
    "btw": {v: round(c, 3) for v, c in nx.betweenness_centrality(TG, normalized=False).items()},
    "pr": {v: round(c, 3) for v, c in nx.pagerank(TG).items()},
    "cc": {v: round(c, 3) for v, c in nx.clustering(TG).items()},
    "apl": round(nx.average_shortest_path_length(TG), 3),
}

OUT["country_ja"] = COUNTRY_JA

json.dump(OUT, open("data/networks.json", "w"), ensure_ascii=False)
for k, v in OUT.items():
    if isinstance(v, dict) and "stats" in v:
        print(k, v["stats"])
