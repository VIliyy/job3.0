# -*- coding: utf-8 -*-
# 小林工具箱 - 数据库模型

from app.models.resume import Resume, ResumeVersion, ResumeCategory, ResumeStatus
from app.models.application import Application, ApplicationStatus
from app.models.jd import JDAnalysis
from app.models.greeting import GreetingTemplate
from app.models.video_task import VideoTask

__all__ = [
    "Resume", "ResumeVersion", "ResumeCategory", "ResumeStatus",
    "Application", "ApplicationStatus",
    "JDAnalysis",
    "GreetingTemplate",
    "VideoTask"
]
