# -*- coding: utf-8 -*-
# 小林工具箱 - 数据库配置
# 支持SQLite（本地）和MySQL（可选）

import logging

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

# 创建引擎
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
    )
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
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
    # 导入所有模型
    from app.models import (
        resume,
        application,
        greeting,
        jd,
        video_task,
        decompose_task,
        agent_chat,
        job_snapshot,
    )

    Base.metadata.create_all(bind=engine)

    if settings.DATABASE_URL.startswith("sqlite"):
        with engine.begin() as conn:
            duplicates = conn.exec_driver_sql(
                "SELECT job_url, COUNT(*) FROM applications "
                "WHERE job_url IS NOT NULL GROUP BY job_url HAVING COUNT(*) > 1"
            ).fetchall()
            if duplicates:
                logger.error(
                    "skipping job_url unique index because duplicate data exists: %s",
                    len(duplicates),
                )
            else:
                conn.exec_driver_sql(
                    "CREATE UNIQUE INDEX IF NOT EXISTS uq_app_job_url "
                    "ON applications (job_url) WHERE job_url IS NOT NULL"
                )

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
