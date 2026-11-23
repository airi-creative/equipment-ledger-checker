#!/usr/bin/env python3
"""備品台帳チェッカー（Python、標準ライブラリのみ）。

CSV の備品台帳を読み込み、次の異常を検出する：
  1. 必須項目（備品ID／名称／現場）の欠落
  2. 備品ID の重複

使い方：py ledger_check.py sample_ledger.csv
実データではなく、サンプル（テスト）データで使う前提。
"""
import csv
import sys

REQUIRED = ["備品ID", "名称", "現場"]


def check(rows):
    problems = []
    seen_ids = {}
    for lineno, row in enumerate(rows, start=2):  # 1行目はヘッダー
        item = row.get("備品ID", "") or f"（{lineno}行目）"
        # 必須項目の欠落
        for field in REQUIRED:
            if not (row.get(field) or "").strip():
                problems.append((lineno, item, f"必須項目「{field}」が空欄"))
        # 備品ID の重複
        item_id = (row.get("備品ID") or "").strip()
        if item_id:
            if item_id in seen_ids:
                problems.append((lineno, item,
                                 f"備品ID が {seen_ids[item_id]}行目と重複"))
            else:
                seen_ids[item_id] = lineno
    return problems


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "sample_ledger.csv"
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    problems = check(rows)
    print(f"台帳 {len(rows)} 件をチェックしました。異常 {len(problems)} 件。")
    for lineno, item, msg in problems:
        print(f"{lineno}行目 {item}：{msg}")


if __name__ == "__main__":
    main()
