import sqlite3
from pathlib import Path

db_path = Path("data/database.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT * FROM measurements")
print(cur.fetchall())

