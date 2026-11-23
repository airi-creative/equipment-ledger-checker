#!/usr/bin/env python3
"""備品台帳チェッカー（Python、標準ライブラリのみ）。

CSV の備品台帳を読み込み、次の異常を検出する：
  1. 必須項目（備品ID／名称／現場）の欠落
  2. 備品ID の重複
  3. 日付フォーマットの不正
  4. 返却予定日を過ぎているのに未返却

使い方：py ledger_check.py sample_ledger.csv
実データではなく、サンプル（テスト）データで使う前提。
"""
import csv
import sys
from datetime import date, datetime

REQUIRED = ["備品ID", "名称", "現場"]
DATE_FIELDS = ["貸出日", "返却予定日", "返却日"]


def parse_date(text):
    """YYYY-MM-DD を date に変換。空欄は None、不正は ValueError。"""
    text = (text or "").strip()
    if text == "":
        return None
    return datetime.strptime(text, "%Y-%m-%d").date()


def check(rows, today):
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
        # 日付の形式チェック
        parsed = {}
        for field in DATE_FIELDS:
            try:
                parsed[field] = parse_date(row.get(field, ""))
            except ValueError:
                problems.append((lineno, item,
                                 f"「{field}」の日付形式が不正：{row.get(field)}"))
                parsed[field] = None
        # 返却期限の超過（未返却のみ）
        due = parsed.get("返却予定日")
        returned = parsed.get("返却日")
        if due is not None and returned is None and due < today:
            problems.append((lineno, item,
                             f"返却予定日 {due} を過ぎても未返却"))
    return problems


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "sample_ledger.csv"
    today = date.today()
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    problems = check(rows, today)
    print(f"台帳 {len(rows)} 件をチェックしました。異常 {len(problems)} 件。")
    for lineno, item, msg in problems:
        print(f"{lineno}行目 {item}：{msg}")


if __name__ == "__main__":
    main()
