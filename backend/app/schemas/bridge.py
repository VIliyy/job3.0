# -*- coding: utf-8 -*-
# Job3.0 求职系统 - 浏览器扩展桥接 Schema（海投助手本地桥 v1.0）

from pydantic import BaseModel, Field
from typing import Optional


class BridgeJobRecordIn(BaseModel):
    """扩展上报的岗位投递记录"""

    job_url: str = Field(..., max_length=512, description="岗位链接（用于去重）")
    company: str = Field(..., min_length=1, max_length=255, description="公司名称")
    position: Optional[str] = Field(None, max_length=255, description="职位名称")
    salary: Optional[str] = Field(None, max_length=100, description="薪资")
    location: Optional[str] = Field(None, max_length=255, description="工作地点")
    source: Optional[str] = Field("boss-zhipin", max_length=100, description="来源平台")
    jd_text: Optional[str] = Field(None, description="JD 原文快照")
    resume_id: Optional[int] = Field(None, description="关联简历 ID，缺省自动选最新简历")
    greeting: Optional[str] = Field(None, description="打招呼文稿（扩展手动编辑后传入）")
    generate_greeting: bool = Field(True, description="是否按 JD 自动生成打招呼文稿")