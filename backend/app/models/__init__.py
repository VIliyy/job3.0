# -*- coding: utf-8 -*-
# Job3.0 求职系统 - 数据库模型（v2.0）

from app.models.resume import Resume, ResumeVersion, ResumeCategory, ResumeStatus
from app.models.application import Application, ApplicationStatus
from app.models.jd import JDAnalysis
from app.models.greeting import GreetingTemplate

__all__ = [
    "Resume", "ResumeVersion", "ResumeCategory", "ResumeStatus",
    "Application", "ApplicationStatus",
    "JDAnalysis",
    "GreetingTemplate"
]
