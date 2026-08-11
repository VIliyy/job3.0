# -*- coding: utf-8 -*-
# Job3.0 ???? - API???v2.0?

from fastapi import APIRouter
from app.api import (
    resume, 
    application, 
    greeting, 
    jd, 
    agent, 
    ai, 
    stream, 
    match, 
    orchestration,
    optimize,
    export
)

api_router = APIRouter()

# v2.0 ????
api_router.include_router(resume.router, tags=["???? v2.0"])
api_router.include_router(application.router, tags=["???? v2.0"])
api_router.include_router(jd.router, tags=["JD?? v2.0"])
api_router.include_router(optimize.router, tags=["????? v2.0"])
api_router.include_router(export.router, tags=["????"])

# ????????
api_router.include_router(greeting.router, prefix="/greeting", tags=["????"])
api_router.include_router(agent.router, prefix="/agent", tags=["Agent??"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI??"])
api_router.include_router(stream.router, prefix="/stream", tags=["????"])
api_router.include_router(match.router, prefix="/match", tags=["????"])
api_router.include_router(orchestration.router, prefix="/orchestration", tags=["?Agent??"])
