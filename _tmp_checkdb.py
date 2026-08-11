# -*- coding: utf-8 -*-
import sys, sqlite3
sys.path.insert(0, r"E:\job3.0\backend")
conn = sqlite3.connect(r"E:\job3.0\backend\job3.db")
cur = conn.cursor()
cur.execute("SELECT id, slot, category, filename FROM resumes")
for row in cur.fetchall():
    print(row)
conn.close()
