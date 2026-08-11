# -*- coding: utf-8 -*-
# Job3.0 求职系统 - 数据库配置
# 支持SQLite（本地）和MySQL（可选）

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 创建引擎
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
    )
    print("[OK] 数据库: SQLite (本地存储)")
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=settings.DEBUG
    )
    print("[OK] 数据库: MySQL")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # v2.0: 导入所有模型
    from app.models import (
        resume, 
        application, 
        greeting, 
        jd
    )
    
    Base.metadata.create_all(bind=engine)

    # 轻量迁移：ResumeVersion.original_content（幂等，SQLite 专用）
    if settings.DATABASE_URL.startswith("sqlite"):
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(engine)
            columns = [c["name"] for c in inspector.get_columns("resume_versions")]
            if "original_content" not in columns:
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE resume_versions ADD COLUMN original_content TEXT"))
                print("[OK] 迁移: resume_versions.original_content 已添加")
        except Exception as e:
            print(f"[WARN] 数据库迁移失败(可忽略，首次启动时表可能不存在): {e}")

    print("[OK] 数据库表创建成功 (v2.0)")


def get_database_url():
    return settings.DATABASE_URL
