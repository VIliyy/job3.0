# -*- coding: utf-8 -*-
import sqlite3, os
conn = sqlite3.connect(r"E:\job3.0\backend\job3.db")
cur = conn.cursor()
rows = cur.execute("SELECT id, filepath FROM resumes").fetchall()
for rid, fp in rows:
    cur.execute("DELETE FROM resume_versions WHERE resume_id=?", (rid,))
    cur.execute("DELETE FROM resumes WHERE id=?", (rid,))
    if fp and os.path.exists(fp):
        os.remove(fp)
        print("removed file:", fp)
conn.commit()
left = cur.execute("SELECT COUNT(*) FROM resumes").fetchone()[0]
print("resumes left:", left)
conn.close()
