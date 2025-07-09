#!/bin/sh
set -e

# DynamoDB Localが起動していることを前提にテーブル作成・サンプルデータ投入
python scripts/init_db.py || true

# FastAPIサーバ起動
uvicorn main:app --host 0.0.0.0 --port 8000 