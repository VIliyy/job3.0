# -*- coding: utf-8 -*-
# 小林工具箱 - 数据库模型

from app.models.resume import Resume, ResumeVersion, ResumeCategory, ResumeStatus
from app.models.application import Application, ApplicationStatus
from app.models.jd import JDAnalysis
from app.models.greeting import GreetingTemplate
from app.models.video_task import VideoTask
from app.models.agent_chat import AgentChat
from app.models.decompose_task import DecomposeTask, DecomposeContract, DecomposeDecision
from app.models.job_snapshot import JobSnapshot

__all__ = [
    "Resume", "ResumeVersion", "ResumeCategory", "ResumeStatus",
    "Application", "ApplicationStatus",
    "JDAnalysis",
    "GreetingTemplate",
    "VideoTask",
    "AgentChat",
    "DecomposeTask", "DecomposeContract", "DecomposeDecision",
    "JobSnapshot"
]
