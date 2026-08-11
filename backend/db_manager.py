# -*- coding: utf-8 -*-
\"\"\"
Job3.0 求职系统 - 数据库管理工具

功能：
1. 查看数据库状态
2. 查看所有表
3. 查看简历记录
4. 查看投递记录
5. 查看打招呼语模板
6. 导出数据
7. 清空数据
\"\"\"

import sqlite3
import os
import json
from datetime import datetime

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), \"job3.db\")

def get_connection():
    \"\"\"获取数据库连接\"\"\"
    if not os.path.exists(DB_PATH):
        print(\"❌ 数据库文件不存在！请先启动后端初始化数据库\")
        return None
    return sqlite3.connect(DB_PATH)

def print_header(title):
    \"\"\"打印标题\"\"\"
    print(\"\n\" + \"=\" * 60)
    print(f\"  {title}\")
    print(\"=\" * 60)

def view_status():
    \"\"\"查看数据库状态\"\"\"
    print_header(\"数据库状态\")
    
    if not os.path.exists(DB_PATH):
        print(\"❌ 数据库文件不存在\")
        return
    
    file_size = os.path.getsize(DB_PATH)
    print(f\"📁 文件位置：{DB_PATH}\")
    print(f\"📊 文件大小：{file_size / 1024:.2f} KB\")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 统计各表记录数
    tables = [\"resumes\", \"applications\", \"greeting_templates\"]
    print(\"\n📋 记录统计：\")
    
    for table in tables:
        try:
            cursor.execute(f\"SELECT COUNT(*) FROM {table}\")
            count = cursor.fetchone()[0]
            print(f\"   • {table}: {count} 条记录\")
        except sqlite3.OperationalError:
            print(f\"   • {table}: 表不存在\")
    
    conn.close()

def view_tables():
    \"\"\"查看所有表\"\"\"
    print_header(\"数据库表\")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f\"\n📑 表名：{table_name}\")
        
        # 查看表结构
        cursor.execute(f\"PRAGMA table_info({table_name})\")
        columns = cursor.fetchall()
        print(\"   列：\")
        for col in columns:
            print(f\"     - {col[1]} ({col[2]})\")
        
        # 查看记录数
        cursor.execute(f\"SELECT COUNT(*) FROM {table_name}\")
        count = cursor.fetchone()[0]
        print(f\"   记录数：{count}\")
    
    conn.close()

def view_resumes():
    \"\"\"查看简历记录\"\"\"
    print_header(\"简历记录\")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(\"\"\"
        SELECT id, slot, filename, version_name, file_size, is_active, created_at
        FROM resumes
        ORDER BY slot
    \"\"\")
    
    rows = cursor.fetchall()
    
    if not rows:
        print(\"📭 暂无简历记录\")
    else:
        for row in rows:
            print(f\"\n📄 简历 #{row[0]}\")
            print(f\"   槽位：{row[1]}\")
            print(f\"   文件名：{row[2]}\")
            print(f\"   版本名：{row[3] or '未命名'}\")
            print(f\"   文件大小：{row[4]} bytes\")
            print(f\"   当前使用：{'是' if row[5] else '否'}\")
            print(f\"   创建时间：{row[6]}\")
    
    conn.close()

def view_applications():
    \"\"\"查看投递记录\"\"\"
    print_header(\"投递记录\")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(\"\"\"
        SELECT id, company, position, status, salary, created_at
        FROM applications
        ORDER BY created_at DESC
    \"\"\")
    
    rows = cursor.fetchall()
    
    if not rows:
        print(\"📭 暂无投递记录\")
    else:
        status_map = {
            \"pending\": \"待处理\",
            \"viewed\": \"已查看\",
            \"interview\": \"面试中\",
            \"offer\": \"Offer\",
            \"rejected\": \"已拒绝\",
            \"withdrawn\": \"已撤回\"
        }
        
        for row in rows:
            print(f\"\n🏢 投递 #{row[0]}\")
            print(f\"   公司：{row[1]}\")
            print(f\"   岗位：{row[2] or '未知'}\")
            print(f\"   状态：{status_map.get(row[3], row[3])}\")
            print(f\"   薪资：{row[4] or '未知'}\")
            print(f\"   时间：{row[5]}\")
    
    conn.close()

def view_greetings():
    \"\"\"查看打招呼语模板\"\"\"
    print_header(\"打招呼语模板\")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(\"\"\"
        SELECT id, name, content, is_default, created_at
        FROM greeting_templates
        ORDER BY is_default DESC, created_at DESC
    \"\"\")
    
    rows = cursor.fetchall()
    
    if not rows:
        print(\"📭 暂无模板\")
    else:
        for row in rows:
            print(f\"\n📝 模板 #{row[0]}\")
            print(f\"   名称：{row[1]}\")
            print(f\"   内容：{row[2][:50]}...\")
            print(f\"   默认模板：{'是' if row[3] else '否'}\")
            print(f\"   创建时间：{row[4]}\")
    
    conn.close()

def export_data():
    \"\"\"导出数据\"\"\"
    print_header(\"导出数据\")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    data = {}
    
    # 导出简历
    cursor.execute(\"SELECT * FROM resumes\")
    data[\"resumes\"] = cursor.fetchall()
    
    # 导出投递记录
    cursor.execute(\"SELECT * FROM applications\")
    data[\"applications\"] = cursor.fetchall()
    
    # 导出模板
    cursor.execute(\"SELECT * FROM greeting_templates\")
    data[\"greeting_templates\"] = cursor.fetchall()
    
    # 保存到文件
    export_file = f\"job3_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json\"
    with open(export_file, \"w\", encoding=\"utf-8\") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f\"[OK] 数据已导出到：{export_file}\")
    
    conn.close()

def clear_data():
    \"\"\"清空数据\"\"\"
    print_header(\"清空数据\")
    
    confirm = input(\"[WARN] 确认清空所有数据？（输入 'yes' 确认）：\")
    
    if confirm.lower() != \"yes\":
        print(\"❌ 已取消\")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(\"DELETE FROM resumes\")
    cursor.execute(\"DELETE FROM applications\")
    cursor.execute(\"DELETE FROM greeting_templates\")
    
    conn.commit()
    conn.close()
    
    print(\"[OK] 数据已清空\")

def main():
    \"\"\"主菜单\"\"\"
    while True:
        print_header(\"Job3.0 数据库管理工具\")
        
        print(\"\n请选择操作：\")
        print(\"  1. 查看数据库状态\")
        print(\"  2. 查看所有表\")
        print(\"  3. 查看简历记录\")
        print(\"  4. 查看投递记录\")
        print(\"  5. 查看打招呼语模板\")
        print(\"  6. 导出数据\")
        print(\"  7. 清空数据\")
        print(\"  0. 退出\")
        
        choice = input(\"\n请输入选项：\")
        
        if choice == \"1\":
            view_status()
        elif choice == \"2\":
            view_tables()
        elif choice == \"3\":
            view_resumes()
        elif choice == \"4\":
            view_applications()
        elif choice == \"5\":
            view_greetings()
        elif choice == \"6\":
            export_data()
        elif choice == \"7\":
            clear_data()
        elif choice == \"0\":
            print(\"\n👋 再见！\")
            break
        else:
            print(\"\n❌ 无效选项，请重新选择\")

if __name__ == \"__main__\":
    main()
