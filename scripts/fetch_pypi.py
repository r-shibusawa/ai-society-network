"""PyPI から主要AIライブラリの依存関係（必須依存のみ）を幅優先で取得する"""
import json, re, time, requests, sys
from collections import deque

SEEDS = ["transformers", "torch", "tensorflow", "keras", "jax", "scikit-learn", "langchain",
         "langchain-openai", "openai", "anthropic", "google-genai", "llama-index", "diffusers",
         "accelerate", "datasets", "sentence-transformers", "vllm", "ollama", "gradio", "streamlit",
         "huggingface-hub", "tokenizers", "peft", "trl", "xgboost", "lightgbm", "opencv-python",
         "ultralytics", "spacy", "nltk", "pandas", "matplotlib", "chromadb", "faiss-cpu",
         "tiktoken", "mcp", "crewai", "autogen-agentchat", "litellm", "onnxruntime"]
MAX_DEPTH = 3

def norm(n):
    return re.sub(r"[-_.]+", "-", n).lower()

def req_names(info):
    out = set()
    for r in info.get("requires_dist") or []:
        if "extra ==" in r.replace("extra==", "extra =="):
            continue
        name = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", r)
        if name:
            out.add(norm(name.group(1)))
    return sorted(out)

pkgs, q = {}, deque((norm(s), 0) for s in SEEDS)
seen = set(x for x, _ in q)
while q:
    name, d = q.popleft()
    try:
        r = requests.get(f"https://pypi.org/pypi/{name}/json", timeout=30)
        if r.status_code != 200:
            print("skip", name, r.status_code, file=sys.stderr); continue
        info = r.json()["info"]
    except Exception as e:
        print("err", name, e, file=sys.stderr); continue
    deps = req_names(info)
    pkgs[name] = {"version": info["version"], "summary": (info.get("summary") or "")[:140],
                  "deps": deps, "depth": d, "seed": d == 0}
    if d < MAX_DEPTH:
        for x in deps:
            if x not in seen:
                seen.add(x); q.append((x, d + 1))
    time.sleep(0.05)
json.dump(pkgs, open("data/raw/pypi_deps.json", "w"), ensure_ascii=False)
print(len(pkgs))
