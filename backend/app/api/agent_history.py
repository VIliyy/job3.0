# -*- coding: utf-8 -*-
"""
求职助手聊天历史 API（小林工具箱）
GET    /api/agent/history          会话列表
GET    /api/agent/history/{id}     会话详情（含消息）
POST   /api/agent/history          新建或更新会话
DELETE /api/agent/history/{id}     删除单个会话
DELETE /api/agent/history          清空全部历史
"""
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.agent_chat import AgentChat
from app.schemas.agent_history import AgentChatIn, AgentChatBrief, AgentChatDetail

router = APIRouter(prefix="/agent/history", tags=["求职助手"])


def _detail(chat: AgentChat) -> AgentChatDetail:
    messages = chat.get_messages()
    return AgentChatDetail(
        chat_id=chat.chat_id,
        title=chat.title or "",
        message_count=len(messages),
        updated_at=chat.updated_at,
        messages=messages,
    )


@router.get("", response_model=list[AgentChatBrief])
def list_chats(limit: int = 50, db: Session = Depends(get_db)):
    chats = db.query(AgentChat).order_by(AgentChat.updated_at.desc()).limit(min(limit, 200)).all()
    return [AgentChatBrief(
        chat_id=c.chat_id,
        title=c.title or "",
        message_count=len(c.get_messages()),
        updated_at=c.updated_at,
    ) for c in chats]


@router.post("", response_model=AgentChatDetail)
def save_chat(data: AgentChatIn, db: Session = Depends(get_db)):
    messages_json = json.dumps([m.model_dump() for m in data.messages], ensure_ascii=False)
    title = (data.title or "").strip()[:128]
    if data.chat_id:
        chat = db.query(AgentChat).filter(AgentChat.chat_id == data.chat_id).first()
        if chat:
            chat.messages_json = messages_json
            if title:
                chat.title = title
            db.commit()
            db.refresh(chat)
            return _detail(chat)
    chat = AgentChat(
        chat_id=data.chat_id or uuid.uuid4().hex[:16],
        title=title,
        messages_json=messages_json,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return _detail(chat)


@router.delete("")
def clear_chats(db: Session = Depends(get_db)):
    db.query(AgentChat).delete()
    db.commit()
    return {"ok": True}


@router.get("/{chat_id}", response_model=AgentChatDetail)
def get_chat(chat_id: str, db: Session = Depends(get_db)):
    chat = db.query(AgentChat).filter(AgentChat.chat_id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="会话不存在")
    return _detail(chat)


@router.delete("/{chat_id}")
def delete_chat(chat_id: str, db: Session = Depends(get_db)):
    chat = db.query(AgentChat).filter(AgentChat.chat_id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="会话不存在")
    db.delete(chat)
    db.commit()
    return {"ok": True}