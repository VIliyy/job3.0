# -*- coding: utf-8 -*-
import io

path = r"E:\job3.0\backend\app\api\resume.py"
src = io.open(path, encoding="utf-8").read()

src = src.replace(
    "from pydantic import BaseModel",
    "from pydantic import BaseModel, Field"
)

old = 'router = APIRouter(prefix="/resumes", tags=["简历管理 v2.0"])\n'
new = old + '''

# 兼容中文标签 / 大小写差异 / 非法值，统一映射为枚举值，避免 SQLAlchemy Enum 校验崩溃
_CATEGORY_ALIASES = {
    "tech": ResumeCategory.TECH, "技术": ResumeCategory.TECH,
    "product": ResumeCategory.PRODUCT, "产品": ResumeCategory.PRODUCT,
    "ops": ResumeCategory.OPERATIONS, "运营": ResumeCategory.OPERATIONS,
    "marketing": ResumeCategory.MARKETING, "市场": ResumeCategory.MARKETING,
    "other": ResumeCategory.OTHER, "其他": ResumeCategory.OTHER,
}
_STATUS_ALIASES = {
    "draft": ResumeStatus.DRAFT, "草稿": ResumeStatus.DRAFT,
    "processing": ResumeStatus.PROCESSING, "处理中": ResumeStatus.PROCESSING,
    "optimized": ResumeStatus.OPTIMIZED, "已优化": ResumeStatus.OPTIMIZED,
    "applied": ResumeStatus.APPLIED, "已投递": ResumeStatus.APPLIED,
    "archived": ResumeStatus.ARCHIVED, "已归档": ResumeStatus.ARCHIVED,
}


def normalize_category(category) -> ResumeCategory:
    if isinstance(category, ResumeCategory):
        return category
    key = str(category or "").strip().lower()
    return _CATEGORY_ALIASES.get(key, ResumeCategory.OTHER)


def normalize_status(status) -> ResumeStatus:
    if isinstance(status, ResumeStatus):
        return status
    key = str(status or "").strip().lower()
    return _STATUS_ALIASES.get(key, ResumeStatus.DRAFT)
'''
assert old in src, "router anchor"
src = src.replace(old, new)

old = "        category=resume_data.category,\n"
assert old in src, "create_resume"
src = src.replace(old, "        category=normalize_category(resume_data.category),\n", 1)

old = """    if category:
        query = query.filter(Resume.category == category)
    if status:
        query = query.filter(Resume.status == status)"""
new = """    if category:
        query = query.filter(Resume.category == normalize_category(category))
    if status:
        query = query.filter(Resume.status == normalize_status(status))"""
assert old in src, "list_resumes"
src = src.replace(old, new)

old = """    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(resume, field, value)"""
new = """    update_dict = update_data.model_dump(exclude_unset=True)
    if "category" in update_dict:
        update_dict["category"] = normalize_category(update_dict["category"])
    if "status" in update_dict:
        update_dict["status"] = normalize_status(update_dict["status"])
    for field, value in update_dict.items():
        setattr(resume, field, value)"""
assert old in src, "update_resume"
src = src.replace(old, new)

old = "        category=category, version_name=version_name\n    )\n    return resume"
new = "        category=normalize_category(category), version_name=version_name\n    )\n    return resume"
count = src.count(old)
assert count == 2, f"save/upload anchors: {count}"
src = src.replace(old, new)

old = """class SaveTextRequest(BaseModel):
    slot: int = 1
    content: str
    category: str = "other"
    version_name: Optional[str] = None"""
new = """class SaveTextRequest(BaseModel):
    slot: int = Field(1, ge=1, le=4)
    content: str
    category: str = "other"
    version_name: Optional[str] = None"""
assert old in src, "SaveTextRequest"
src = src.replace(old, new)

io.open(path, "w", encoding="utf-8", newline="\n").write(src)
print("PATCH OK")
