# -*- coding: utf-8 -*-
# 信息拆解模块 - 数据模型（契约：docs/拆解契约.md 第 9 章）

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class DecomposeTask(Base):
    """拆解任务主表"""
    __tablename__ = "decompose_tasks"

    __table_args__ = (
        Index("idx_decompose_task_updated", "updated_at"),
        {"sqlite_autoincrement": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="未命名拆解")
    state = Column(String(32), nullable=False, default="DRAFT")
    version = Column(Integer, nullable=False, default=1)
    source_content = Column(Text, nullable=False)
    source_target = Column(String(500), nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    contracts = relationship(
        "DecomposeContract",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="DecomposeContract.id"
    )
    decisions = relationship(
        "DecomposeDecision",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="DecomposeDecision.id"
    )


class DecomposeContract(Base):
    """契约表：每段流水线一份，版本化（乐观锁）"""
    __tablename__ = "decompose_contracts"

    __table_args__ = (
        Index("idx_decompose_contract_task_name", "task_id", "contract_name"),
        {"sqlite_autoincrement": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("decompose_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    contract_name = Column(String(10), nullable=False)  # S0 / S1 / S2 / S3
    version = Column(Integer, nullable=False, default=1)
    status = Column(String(20), nullable=False, default="auto_ok")  # auto_ok / needs_human / human_approved
    body = Column(Text, nullable=False, default="{}")  # JSON: facts + inferences + meta
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("DecomposeTask", back_populates="contracts")


class DecomposeDecision(Base):
    """人的确认/意见留痕"""
    __tablename__ = "decompose_decisions"

    __table_args__ = (
        Index("idx_decompose_decision_task", "task_id"),
        {"sqlite_autoincrement": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("decompose_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    gate = Column(String(4), nullable=False)  # A / B / C
    action = Column(String(20), nullable=False)  # approve / regenerate
    note = Column(Text, nullable=True)
    decided_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("DecomposeTask", back_populates="decisions")
