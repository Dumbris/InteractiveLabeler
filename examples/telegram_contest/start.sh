#!/bin/sh

set -e

pip3 install -r requirements.txt

cat data/news_en.jsonl | python3 main.py >> news_en_labeled.jsonl

