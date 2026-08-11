import sqlite3
import os
import shutil

db_path = "job3.db"
backup_path = db_path + ".sensitive_backup.db"

# 先备份
if os.path.exists(db_path):
    shutil.copy(db_path, backup_path)
    print("数据库已备份到:", backup_path)

# 重新创建数据库连接
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print("当前表:", tables)

# 删除简历数据
try:
    cursor.execute("DELETE FROM resumes")
    print("resumes 表已清空")
except Exception as e:
    print("resumes 表清理:", e)

try:
    cursor.execute("DELETE FROM greeting_templates")
    print("greeting_templates 表已清空")
except Exception as e:
    print("greeting_templates 表清理:", e)

try:
    cursor.execute("DELETE FROM applications")
    print("applications 表已清空")
except Exception as e:
    print("applications 表清理:", e)

conn.commit()
conn.close()
print("数据库清理完成")
