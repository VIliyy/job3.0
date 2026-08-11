# -*- coding: utf-8 -*-
"""
Pytest 配置文件
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db


# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_resume():
    """示例简历数据"""
    return """
    张三
    软件工程师
    
    教育背景:
    - 清华大学 计算机科学 硕士 2018-2021
    - 北京大学 计算机科学 学士 2014-2018
    
    工作经历:
    - 字节跳动 高级工程师 2021-至今
      - 负责抖音推荐系统开发
      - 使用Python、Golang
    
    技能:
    - Python, Golang, Java
    - Redis, MySQL, MongoDB
    """


@pytest.fixture
def sample_jd():
    """示例JD数据"""
    return """
    【字节跳动】高级后端工程师
    
    职位描述:
    负责抖音核心业务系统开发
    
    要求:
    - 3年以上后端开发经验
    - 精通Python或Go
    - 有大型系统开发经验
    - 熟悉分布式系统
    
    加分项:
    - 有推荐系统经验
    - 开源项目贡献者
    """
