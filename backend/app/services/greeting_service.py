# -*- coding: utf-8 -*-
"""
Job3.0 求职系统 - 打招呼语服务
"""

from sqlalchemy.orm import Session
from typing import Optional, List, Dict
import re

from app.models.greeting import GreetingTemplate
from app.schemas.greeting import (
    GreetingTemplateCreate, GreetingTemplateUpdate, GreetingTemplateResponse,
    GreetingGenerateRequest, GreetingGenerateResponse
)

class GreetingService:
    """打招呼语服务"""
    
    # 支持的模板变量
    TEMPLATE_VARIABLES = {
        "{岗位}": "job_title",
        "{公司}": "company",
        "{年限}": "experience",
        "{技能}": "skills",
        "{方向}": "direction",
        "{学历}": "education",
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    async def list_templates(self) -> List[GreetingTemplate]:
        """获取模板列表"""
        return self.db.query(GreetingTemplate).order_by(
            GreetingTemplate.is_default.desc(),
            GreetingTemplate.created_at.desc()
        ).all()
    
    async def create_template(self, data: GreetingTemplateCreate) -> GreetingTemplate:
        """创建模板"""
        # 如果设为默认，先取消其他默认
        if data.is_default:
            self.db.query(GreetingTemplate).update({"is_default": False})
        
        template = GreetingTemplate(
            name=data.name,
            content=data.content,
            is_default=data.is_default
        )
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        
        return template
    
    async def update_template(
        self, 
        template_id: int, 
        update_data: GreetingTemplateUpdate
    ) -> Optional[GreetingTemplate]:
        """更新模板"""
        template = self.db.query(GreetingTemplate).filter(
            GreetingTemplate.id == template_id
        ).first()
        
        if template:
            if update_data.is_default and not template.is_default:
                # 设为默认时，先取消其他默认
                self.db.query(GreetingTemplate).filter(
                    GreetingTemplate.id != template_id
                ).update({"is_default": False})
            
            if update_data.name is not None:
                template.name = update_data.name
            if update_data.content is not None:
                template.content = update_data.content
            if update_data.is_default is not None:
                template.is_default = update_data.is_default
            
            self.db.commit()
            self.db.refresh(template)
        
        return template
    
    async def delete_template(self, template_id: int) -> bool:
        """删除模板"""
        template = self.db.query(GreetingTemplate).filter(
            GreetingTemplate.id == template_id
        ).first()
        
        if template:
            self.db.delete(template)
            self.db.commit()
            return True
        
        return False
    
    async def generate_greeting(self, request: GreetingGenerateRequest) -> GreetingGenerateResponse:
        """根据JD生成打招呼语"""
        # 获取模板
        if request.template_id:
            template = self.db.query(GreetingTemplate).filter(
                GreetingTemplate.id == request.template_id
            ).first()
        else:
            # 使用默认模板
            template = self.db.query(GreetingTemplate).filter(
                GreetingTemplate.is_default == True
            ).first()
        
        if not template:
            # 如果没有模板，生成默认打招呼语
            greeting = f"您好！我对贵公司的{self._extract_position(request.jd_content)}职位很感兴趣，希望能有机会进一步沟通。"
            return GreetingGenerateResponse(
                greeting=greeting,
                template_name="默认",
                variables_used={}
            )
        
        # 提取变量
        variables = self._extract_variables(request.jd_content, request.resume_content)
        
        # 替换模板中的变量
        greeting = template.content
        for var_name, var_value in variables.items():
            greeting = greeting.replace(var_name, var_value)
        
        return GreetingGenerateResponse(
            greeting=greeting,
            template_name=template.name,
            variables_used=variables
        )
    
    def _extract_variables(self, jd_content: str, resume_content: str = None) -> Dict[str, str]:
        """从JD和简历中提取变量"""
        variables = {}
        
        # 提取公司名
        company_match = re.search(r'公司[：:]\s*([^\n，,]+)', jd_content)
        if company_match:
            variables["{公司}"] = company_match.group(1)
        else:
            # 尝试从职位名称推断
            variables["{公司}"] = "贵公司"
        
        # 提取岗位名
        position = self._extract_position(jd_content)
        variables["{岗位}"] = position
        
        # 提取技能（简化版）
        skills = ", ".join(re.findall(r'[A-Za-z+#]+', jd_content)[:5])
        variables["{技能}"] = skills if skills else "相关技能"
        
        # 提取年限
        exp_match = re.search(r'(\d+)\s*年', jd_content)
        variables["{年限}"] = exp_match.group(1) + "年" if exp_match else "相关"
        
        # 提取学历
        edu_match = re.search(r'(本科|硕士|博士|大专|高中|中专)', jd_content)
        variables["{学历}"] = edu_match.group(1) if edu_match else "本科"
        
        return variables
    
    def _extract_position(self, text: str) -> str:
        """提取职位名称"""
        # 常见职位名称模式
        patterns = [
            r'招聘[：:]\s*([^\n，,]+)',
            r'职位[：:]\s*([^\n，,]+)',
            r'岗位[：:]\s*([^\n，,]+)',
            r'([^\n，,]*开发[^\n，,]*?)工程师',
            r'([^\n，,]*经理[^\n，,]*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return "相关"
