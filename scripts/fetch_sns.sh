#!/bin/sh
# SNS 関連の公開データセットをダウンロードする（data/raw/ 以下）
set -e
cd "$(dirname "$0")/.."
mkdir -p data/raw/fb data/raw/polblogs data/raw/pheme data/raw/twitter
# SNAP ego-Facebook（McAuley & Leskovec, 2012）
curl -sL -o data/raw/fb/facebook.tar.gz https://snap.stanford.edu/data/facebook.tar.gz
tar xzf data/raw/fb/facebook.tar.gz -C data/raw/fb
# SNAP ego-Twitter（フォロー関係，スライドの「多数派の錯覚」の集計に使用）
curl -sL -o data/raw/twitter/twitter_combined.txt.gz https://snap.stanford.edu/data/twitter_combined.txt.gz
# 政治ブログ（Adamic & Glance, 2005）
curl -sL -o data/raw/polblogs/polblogs.zip https://public.websites.umich.edu/~mejn/netdata/polblogs.zip
unzip -o -q data/raw/polblogs/polblogs.zip -d data/raw/polblogs
# PHEME（Zubiaga et al., 2016）を整形した CSV（steve-kasica/pheme-rnr-knowledge-discovery）
B=https://raw.githubusercontent.com/steve-kasica/pheme-rnr-knowledge-discovery/master/data/tweets
for e in charliehebdo ferguson germanwings-crash ottawashooting sydneysiege; do
  curl -sL -o "data/raw/pheme/tweets_$e.csv" "$B/$e.csv"
done
echo "done"
