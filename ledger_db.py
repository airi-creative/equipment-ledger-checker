import csv
import sqlite3

DB_FILE = "ledger.db"
CSV_FILE = "sample_ledger.csv"

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS equipment")
cur.execute("""
CREATE TABLE equipment (
    item_id TEXT,
    name TEXT,
    site TEXT,
    person TEXT,
    checkout_date TEXT,
    due_date TEXT,
    return_date TEXT
)
""")

with open(CSV_FILE, encoding="utf-8", newline="") as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = [row for row in reader if row]
cur.executemany("INSERT INTO equipment VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
conn.commit()
print(f"{len(rows)} 件をDBに取り込みました")

print("\n■ 現場別の件数")
for site, count in cur.execute("""
    SELECT site, COUNT(*) FROM equipment GROUP BY site ORDER BY site
"""):
    print(f"{site or '(現場が空欄)'}: {count} 件")

print("\n■ 未返却の一覧")
for item_id, name, due in cur.execute("""
    SELECT item_id, name, due_date FROM equipment
    WHERE return_date IS NULL OR return_date = ''
    ORDER BY due_date
"""):
    print(f"{item_id} {name}（返却予定: {due}）")

print("\n■ 重複している備品ID")
for item_id, count in cur.execute("""
    SELECT item_id, COUNT(*) FROM equipment
    GROUP BY item_id HAVING COUNT(*) > 1
"""):
    print(f"{item_id}: {count} 件")

conn.close()
