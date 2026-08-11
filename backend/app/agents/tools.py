# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - LangChain Tools 工具集

提供 Agent 可调用的工具，用于自主搜索和操作数据
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import json

from app.models.resume import Resume
from app.models.application import Application
from app.models.greeting import GreetingTemplate
from app.services.resume_service import ResumeService
from app.services.application_service import ApplicationService
from app.services.greeting_service import GreetingService


# ==============================================================================
# 简历工具 (Resume Tools)
# ==============================================================================

def create_resume_tools(db: Session):
    """创建简历相关工具"""

    class ResumeSearchTool:
        """搜索简历工具 - 根据关键词搜索简历内容"""
        name = "resume_search"
        description = """搜索用户上传的简历内容。当用户提到"我的简历"、"简历内容"、"工作经历"、查询简历信息时使用。
        返回简历的完整内容，包括工作经历、技能、项目经验等。

        输入: 搜索关键词（可选，默认为空返回最新简历）
        输出: 简历内容摘要"""

        def __init__(self, db: Session):
            self.db = db

        def run(self, query: str = "") -> str:
            service = ResumeService(self.db)
            resumes = self.db.query(Resume).filter(Resume.content.isnot(None)).all()

            if not resumes:
                return "目前没有上传任何简历。请提示用户先上传简历。"

            # 按更新时间排序，返回最新的
            resumes = sorted(resumes, key=lambda x: x.updated_at or x.created_at, reverse=True)

            results = []
            for resume in resumes:
                content = resume.content or ""
                # 如果有搜索关键词，进行匹配
                if query and query.lower() not in content.lower():
                    continue

                results.append({
                    "slot": resume.slot,
                    "filename": resume.filename,
                    "version_name": resume.version_name,
                    "content_preview": content[:500] + "..." if len(content) > 500 else content,
                    "content": content  # 完整内容供分析使用
                })

            if not results:
                return f"没有找到包含「{query}」的简历。"

            # 返回最匹配的简历
            best = results[0]
            return json.dumps({
                "slot": best["slot"],
                "version_name": best["version_name"] or best["filename"],
                "content": best["content"],
                "all_resumes_count": len(results)
            }, ensure_ascii=False, indent=2)

    class ResumeListTool:
        """列出所有简历工具"""
        name = "resume_list"
        description = """列出用户上传的所有简历。用于查看有哪些简历版本可用。

        输入: 无
        输出: 简历列表（槽位、文件名、更新时间）"""

        def __init__(self, db: Session):
            self.db = db

        def run(self) -> str:
            resumes = self.db.query(Resume).all()

            if not resumes:
                return "目前没有上传任何简历。"

            result = []
            for r in resumes:
                result.append({
                    "槽位": f"版本 {r.slot}",
                    "文件名": r.filename,
                    "版本名": r.version_name or "未命名",
                    "更新时间": str(r.updated_at or r.created_at)[:10],
                    "是否使用中": "✓" if r.is_active else ""
                })

            return json.dumps(result, ensure_ascii=False, indent=2)

    class ResumeMatchTool:
        """简历-JD匹配工具"""
        name = "resume_match_jd"
        description = """分析简历与职位描述的匹配度。需要同时提供简历内容和JD内容。

        输入: JSON格式 {"resume": "简历内容", "jd": "职位描述"}
        输出: 匹配分析结果（分数、匹配项、缺失项、建议）"""

        def __init__(self, db: Session):
            self.db = db

        async def arun(self, resume: str, jd: str) -> str:
            from app.services.resume_service import ResumeService
            service = ResumeService(self.db)
            result = await service.optimize_resume(resume, jd)
            return json.dumps(result, ensure_ascii=False, indent=2)

        def run(self, resume: str, jd: str) -> str:
            return "请使用异步方式调用: await resume_match_tool.arun(resume, jd)"

    return {
        "resume_search": ResumeSearchTool(db),
        "resume_list": ResumeListTool(db),
        "resume_match": ResumeMatchTool(db)
    }


# ==============================================================================
# 投递记录工具 (Application Tools)
# ==============================================================================

def create_application_tools(db: Session):
    """创建投递记录相关工具"""

    class ApplicationListTool:
        """列出投递记录工具"""
        name = "application_list"
        description = """查看用户的求职投递记录。获取投递过的公司、岗位、状态等信息。

        输入: 筛选条件（可选，如 status="面试中"）
        输出: 投递记录列表"""

        def __init__(self, db: Session):
            self.db = db

        def run(self, status: str = None) -> str:
            query = self.db.query(Application)

            if status:
                # 根据状态筛选
                status_map = {
                    "待投递": "pending",
                    "已投递": "applied",
                    "面试中": "interview",
                    "已Offer": "offer",
                    "已拒绝": "rejected",
                    "已入职": "hired"
                }
                status_value = status_map.get(status, status)
                query = query.filter(Application.status == status_value)

            applications = query.order_by(Application.created_at.desc()).limit(20).all()

            if not applications:
                return "目前没有投递记录。"

            result = []
            for app in applications:
                result.append({
                    "公司": app.company,
                    "岗位": app.position,
                    "状态": app.status,
                    "薪资": app.salary or "未填写",
                    "来源": app.source or "未知",
                    "投递时间": str(app.created_at)[:10]
                })

            return json.dumps(result, ensure_ascii=False, indent=2)

    class ApplicationSearchTool:
        """搜索投递记录工具"""
        name = "application_search"
        description = """搜索特定公司的投递记录。用于检查是否重复投递、查看特定公司状态。

        输入: 公司名称（支持模糊搜索）
        输出: 匹配的投递记录"""

        def __init__(self, db: Session):
            self.db = db

        def run(self, company: str) -> str:
            # 模糊搜索公司名
            apps = self.db.query(Application).filter(
                Application.company.contains(company)
            ).all()

            if not apps:
                return f"没有找到向「{company}」投递的记录。"

            result = [{
                "公司": app.company,
                "岗位": app.position,
                "状态": app.status,
                "薪资": app.salary or "未填写",
                "备注": app.notes or ""
            } for app in apps]

            return json.dumps(result, ensure_ascii=False, indent=2)

    class ApplicationCheckDuplicateTool:
        """检查重复投递工具"""
        name = "application_check_duplicate"
        description = """检查是否重复投递某个公司。用于求职提醒，避免重复投递。

        输入: 公司名称
        输出: 是否重复投递的检查结果"""

        def __init__(self, db: Session):
            self.db = db

        def run(self, company: str) -> str:
            existing = self.db.query(Application).filter(
                Application.company.contains(company)
            ).first()

            if existing:
                return json.dumps({
                    "is_duplicate": True,
                    "company": existing.company,
                    "position": existing.position,
                    "status": existing.status,
                    "message": f"⚠️ 您已投递过该公司（{existing.position}，状态：{existing.status}）"
                }, ensure_ascii=False, indent=2)
            else:
                return json.dumps({
                    "is_duplicate": False,
                    "message": f"✅ 可以投递「{company}」，暂无重复记录"
                }, ensure_ascii=False, indent=2)

    return {
        "application_list": ApplicationListTool(db),
        "application_search": ApplicationSearchTool(db),
        "application_check_duplicate": ApplicationCheckDuplicateTool(db)
    }


# ==============================================================================
# 打招呼语工具 (Greeting Tools)
# ==============================================================================

def create_greeting_tools(db: Session):
    """创建打招呼语相关工具"""

    class GreetingTemplateListTool:
        """列出打招呼语模板工具"""
        name = "greeting_template_list"
        description = """查看用户保存的打招呼语模板。获取可用的模板列表。

        输入: 无
        输出: 打招呼语模板列表"""

        def __init__(self, db: Session):
            self.db = db

        def run(self) -> str:
            templates = self.db.query(GreetingTemplate).all()

            if not templates:
                return "目前没有打招呼语模板。"

            result = []
            for t in templates:
                result.append({
                    "ID": t.id,
                    "名称": t.name,
                    "内容预览": (t.content[:100] + "...") if len(t.content) > 100 else t.content,
                    "是否默认": "✓" if t.is_default else ""
                })

            return json.dumps(result, ensure_ascii=False, indent=2)

    class GreetingGenerateTool:
        """生成打招呼语工具"""
        name = "greeting_generate"
        description = """根据简历和JD生成打招呼语。需要提供公司名、岗位名、简历内容。

        输入: JSON格式 {"company": "公司名", "position": "岗位名", "resume": "简历内容"}
        输出: 生成的打招呼语（支持多平台）"""

        def __init__(self, db: Session):
            self.db = db

        async def arun(self, company: str, position: str, resume: str = "") -> str:
            from app.services.greeting_service import GreetingService
            service = GreetingService(self.db)

            # 简单生成打招呼语
            greeting_data = {
                "company_name": company,
                "position": position,
                "jd_content": f"岗位: {position}",
                "resume_content": resume
            }

            result = await service.generate_greeting(greeting_data)
            return json.dumps(result, ensure_ascii=False, indent=2)

        def run(self, company: str, position: str, resume: str = "") -> str:
            # 同步版本 - 返回提示
            return f"正在生成向「{company}」投递「{position}」岗位的打招呼语..."

    return {
        "greeting_template_list": GreetingTemplateListTool(db),
        "greeting_generate": GreetingGenerateTool(db)
    }


# ==============================================================================
# 工具注册表
# ==============================================================================

def get_all_tools(db: Session) -> List:
    """获取所有可用的工具"""
    tools = []

    # 简历工具
    resume_tools = create_resume_tools(db)
    tools.extend(resume_tools.values())

    # 投递工具
    application_tools = create_application_tools(db)
    tools.extend(application_tools.values())

    # 打招呼语工具
    greeting_tools = create_greeting_tools(db)
    tools.extend(greeting_tools.values())

    return tools


def get_tools_dict(db: Session) -> Dict[str, Any]:
    """获取工具字典（名称 -> 工具）"""
    tools = {}

    tools.update(create_resume_tools(db))
    tools.update(create_application_tools(db))
    tools.update(create_greeting_tools(db))

    return tools
