# Job3.0 RAG 知识检索系统架构设计

**版本**: 1.0.0
**制定时间**: 2026-08-07
**目标**: 为简历优化系统添加RAG能力，实现语义检索和知识增强
**开发者**: 林育丞

---

## 1. 项目概述

### 1.1 背景

当前的Job3.0多Agent协作系统直接使用LLM能力进行简历优化，但存在以下问题：
- 缺乏领域知识支撑，优化建议不够专业
- 无法利用历史优化经验，复用性差
- 缺乏职位技能知识图谱，难以精准匹配

### 1.2 目标

构建基于RAG（检索增强生成）的知识检索系统，实现：
- 领域知识库支持（职位技能、最佳实践、面试题库）
- 历史优化经验复用
- 简历与JD的语义匹配
- 混合检索（向量+关键词）

---

## 2. 技术架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      用户交互层 (Vue 3)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph 状态机编排层                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    StateGraph (主编排器)                   │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │   │
│  │  │ Resume    │  │ JD        │  │ RAG Retrieval      │  │   │
│  │  │ Analysis  │──▶│ Parse     │──▶│ (Knowledge Search) │  │   │
│  │  └────────────┘  └────────────┘  └────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAG 知识检索层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ 向量存储      │  │ 关键词索引    │  │ 混合检索器    │        │
│  │ (ChromaDB)   │  │ (BM25)       │  │ (RRF Fusion) │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      知识库层                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ 职位技能库   │  │ 优化经验库    │  │ 面试题库     │        │
│  │ (JobSkills)  │  │ (OptimExp)   │  │ (IntQuestions)│        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ 最佳实践库   │  │ 行业知识库    │  │ 公司信息库   │        │
│  │ (BestPracs)  │  │ (IndustryKB)  │  │ (Companies) │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      嵌入模型层 (Embedding)                       │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ OpenAI      │  │ 本地模型      │                            │
│  │ text-embedding-3  │  │ (sentence-transformers)  │          │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| 向量数据库 | ChromaDB | 轻量级、易部署 |
| 嵌入模型 | text-embedding-3-small | OpenAI最新模型 |
| 检索框架 | LangChain | RAG编排 |
| 混合检索 | BM25 + 向量 | RRF融合 |
| 后端 | FastAPI | 高性能API |
| 前端 | Vue 3 | 用户界面 |

---

## 3. 知识库设计

### 3.1 职位技能库 (JobSkills)

#### 数据结构
```json
{
  "id": "skill_python",
  "skill_name": "Python",
  "category": "编程语言",
  "level": "初级/中级/高级",
  "related_skills": ["Django", "Flask", "数据分析"],
  "job_titles": ["后端开发工程师", "全栈开发工程师"],
  "importance": "must/higher/nice_to_have",
  "description": "技能描述",
  "learning_resources": ["资源链接"],
  "common_questions": ["常见面试问题"],
  "best_practices": ["最佳实践"]
}
```

#### 用途
- 识别简历中的技能匹配度
- 推荐相关技能
- 生成技能差距分析

### 3.2 优化经验库 (OptimizationExperience)

#### 数据结构
```json
{
  "id": "opt_exp_001",
  "resume_type": "技术简历/管理简历",
  "job_position": "后端开发工程师",
  "industry": "互联网",
  "problem": "简历问题描述",
  "solution": "优化方案",
  "result": {
    "before_score": 65,
    "after_score": 82,
    "improvement": 17
  },
  "star_examples": ["STAR法则示例"],
  "keywords_added": ["关键词添加"],
  "metrics_quantified": ["量化指标"]
}
```

#### 用途
- 复用历史优化经验
- 推荐相似问题的解决方案
- 生成优化建议

### 3.3 面试题库 (InterviewQuestions)

#### 数据结构
```json
{
  "id": "int_q_001",
  "question": "面试问题",
  "topic": "技术主题",
  "difficulty": "easy/medium/hard",
  "job_positions": ["相关职位"],
  "type": "technical/behavioral/case",
  "expected_answer": "期望回答",
  "follow_up_questions": ["追问"],
  "tips": ["回答技巧"]
}
```

#### 用途
- 生成针对性面试题
- 提供回答建议
- 模拟面试练习

### 3.4 行业知识库 (IndustryKnowledge)

#### 数据结构
```json
{
  "id": "industry_ai",
  "industry_name": "人工智能",
  "hot_skills": ["热门技能"],
  "salary_range": "薪资范围",
  "company_list": ["知名公司"],
  "career_paths": ["职业路径"],
  "trends": ["行业趋势"],
  "certifications": ["认证"]
}
```

#### 用途
- 提供行业背景知识
- 薪资行情参考
- 职业发展建议

---

## 4. RAG 检索流程

### 4.1 检索流程

```python
async def rag_retrieval(query: str, top_k: int = 5):
    """
    RAG检索主流程
    """
    # 1. 查询理解
    query_embedding = await embed_model.embed(query)
    
    # 2. 向量检索
    vector_results = await vector_db.similarity_search(
        query_embedding,
        n_results=top_k
    )
    
    # 3. 关键词检索 (BM25)
    bm25_results = await bm25_index.search(query, top_k)
    
    # 4. 混合检索 (RRF Fusion)
    fused_results = rrf_fusion(
        vector_results,
        bm25_results,
        k=60  # RRF参数
    )
    
    # 5. 重排序
    reranked = await reranker.rerank(fused_results, query)
    
    # 6. 上下文组装
    context = assemble_context(reranked)
    
    return context
```

### 4.2 RRF融合算法

```python
def rrf_fusion(results_list: List[List], k: int = 60):
    """
    Reciprocal Rank Fusion (RRF)
    RRF = Σ(1 / (k + rank))
    """
    scores = defaultdict(float)
    
    for results in results_list:
        for rank, item in enumerate(results):
            scores[item.id] += 1 / (k + rank + 1)
    
    # 按分数排序
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    return [item for item, score in sorted_items]
```

### 4.3 Prompt增强

```python
RAG_ENHANCED_PROMPT = """
你是一个专业的简历优化顾问。结合以下知识库内容，帮我优化简历。

## 用户查询：
{query}

## 知识库检索结果：
{context}

## 简历内容：
{resume_text}

## 目标职位JD：
{jd_text}

请基于知识库内容和简历信息，提供专业的优化建议。
"""
```

---

## 5. 数据库设计

### 5.1 ChromaDB Collections

```python
# 初始化ChromaDB
import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(path="./data/chromadb")

# 创建Collections
collections = {
    "job_skills": client.create_collection(
        name="job_skills",
        metadata={"description": "职位技能知识库"}
    ),
    "optimization_experience": client.create_collection(
        name="optimization_experience", 
        metadata={"description": "优化经验库"}
    ),
    "interview_questions": client.create_collection(
        name="interview_questions",
        metadata={"description": "面试题库"}
    ),
    "industry_knowledge": client.create_collection(
        name="industry_knowledge",
        metadata={"description": "行业知识库"}
    )
}
```

### 5.2 Collection Schema

```python
# 每个Collection的metadata schema
job_skills_schema = {
    "skill_name": "str",
    "category": "str", 
    "level": "str",
    "importance": "str",
    "job_titles": "list[str]"
}

optimization_experience_schema = {
    "resume_type": "str",
    "job_position": "str",
    "industry": "str",
    "before_score": "int",
    "after_score": "int"
}

interview_questions_schema = {
    "question": "str",
    "topic": "str",
    "difficulty": "str",
    "type": "str"
}

industry_knowledge_schema = {
    "industry_name": "str",
    "hot_skills": "list[str]",
    "salary_range": "str"
}
```

---

## 6. API接口设计

### 6.1 检索接口

#### 6.1.1 技能检索
```http
POST /api/rag/skills/search
Content-Type: application/json

{
  "query": "Python后端开发",
  "top_k": 5,
  "filters": {
    "category": "编程语言",
    "level": "中级"
  }
}

响应:
{
  "skills": [
    {
      "id": "skill_python",
      "skill_name": "Python",
      "similarity": 0.92,
      "metadata": {...}
    }
  ]
}
```

#### 6.1.2 经验检索
```http
POST /api/rag/experience/search
Content-Type: application/json

{
  "query": "后端开发工程师简历优化",
  "top_k": 3
}

响应:
{
  "experiences": [
    {
      "id": "opt_exp_001",
      "problem": "...",
      "solution": "...",
      "result": {...},
      "similarity": 0.88
    }
  ]
}
```

#### 6.1.3 面试题检索
```http
POST /api/rag/questions/search
Content-Type: application/json

{
  "query": "Python面试题",
  "difficulty": "medium",
  "limit": 10
}

响应:
{
  "questions": [
    {
      "id": "int_q_001",
      "question": "...",
      "topic": "Python",
      "difficulty": "medium",
      "expected_answer": "..."
    }
  ]
}
```

#### 6.1.4 混合检索
```http
POST /api/rag/hybrid/search
Content-Type: application/json

{
  "query": "简历优化建议",
  "collections": ["job_skills", "optimization_experience"],
  "top_k": 5,
  "use_rerank": true
}

响应:
{
  "results": [
    {
      "id": "...",
      "collection": "job_skills",
      "content": "...",
      "score": 0.95,
      "metadata": {...}
    }
  ],
  "total": 5
}
```

### 6.2 管理接口

#### 6.2.1 添加知识
```http
POST /api/rag/knowledge/add
Content-Type: application/json

{
  "collection": "job_skills",
  "documents": [
    {
      "id": "skill_java",
      "content": "Java编程语言...",
      "metadata": {
        "skill_name": "Java",
        "category": "编程语言"
      }
    }
  ]
}
```

#### 6.2.2 更新知识
```http
PUT /api/rag/knowledge/{id}
Content-Type: application/json

{
  "content": "更新的内容...",
  "metadata": {...}
}
```

#### 6.2.3 删除知识
```http
DELETE /api/rag/knowledge/{id}
```

#### 6.2.4 批量导入
```http
POST /api/rag/knowledge/batch
Content-Type: multipart/form-data

上传JSON或CSV文件批量导入知识
```

---

## 7. 前端集成

### 7.1 组件结构

```
frontend/src/
├── components/
│   ├── rag/
│   │   ├── KnowledgeSearch.vue     # 知识检索组件
│   │   ├── SkillTags.vue           # 技能标签展示
│   │   ├── ExperienceCard.vue     # 经验卡片
│   │   └── QuestionList.vue       # 面试题列表
│   └── ...
│
├── composables/
│   ├── useRAGSearch.js            # RAG检索Hook
│   └── useKnowledgeBase.js       # 知识库Hook
│
└── views/
    ├── KnowledgeBase.vue          # 知识库管理页面
    └── SkillGapAnalysis.vue       # 技能差距分析
```

### 7.2 RAG检索Hook

```javascript
// useRAGSearch.js
import { ref } from 'vue'
import axios from '@/api/index.js'

export function useRAGSearch() {
  const results = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  const searchSkills = async (query, options = {}) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await axios.post('/rag/skills/search', {
        query,
        ...options
      })
      results.value = response.skills
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const searchExperience = async (query, options = {}) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await axios.post('/rag/experience/search', {
        query,
        ...options
      })
      results.value = response.experiences
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const hybridSearch = async (query, options = {}) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await axios.post('/rag/hybrid/search', {
        query,
        ...options
      })
      results.value = response.results
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    results,
    isLoading,
    error,
    searchSkills,
    searchExperience,
    hybridSearch
  }
}
```

---

## 8. 性能优化

### 8.1 嵌入优化
```python
# 批量嵌入
async def batch_embed(texts: List[str], batch_size: int = 100):
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = await embed_model.embed_batch(batch)
        embeddings.extend(batch_embeddings)
    return embeddings
```

### 8.2 缓存策略
```python
# 查询结果缓存
from functools import lru_cache

@lru_cache(maxsize=1000)
async def cached_search(query: str, top_k: int):
    return await rag_retrieval(query, top_k)
```

### 8.3 异步索引
```python
# 后台索引更新
import asyncio

async def index_knowledge_background():
    while True:
        await asyncio.sleep(3600)  # 每小时更新
        await update_embeddings()
```

---

## 9. 部署架构

### 9.1 开发环境
```
前端: localhost:5173
后端: localhost:8000
向量数据库: ChromaDB (SQLite)
```

### 9.2 生产环境
```
前端: Nginx
后端: Uvicorn (多进程)
向量数据库: ChromaDB + PostgreSQL
缓存: Redis
嵌入模型: OpenAI API / 本地部署
```

### 9.3 环境变量
```bash
# .env
OPENAI_API_KEY=sk-xxx
CHROMA_PERSIST_DIRECTORY=./data/chromadb
EMBEDDING_MODEL=text-embedding-3-small
RAG_TOP_K=5
RRF_K=60
```

---

## 10. 测试计划

### 10.1 单元测试
- 嵌入模型测试
- 向量检索测试
- BM25检索测试
- RRF融合测试

### 10.2 集成测试
- API端点测试
- RAG流程测试
- 前后端集成测试

### 10.3 性能测试
- 检索延迟测试
- 并发访问测试
- 大规模数据测试

---

## 11. 数据初始化

### 11.1 职位技能数据
```json
[
  {
    "skill_name": "Python",
    "category": "编程语言",
    "level": "中级",
    "related_skills": ["Django", "Flask", "FastAPI"],
    "job_titles": ["后端开发工程师", "全栈开发工程师"],
    "importance": "must"
  },
  {
    "skill_name": "JavaScript", 
    "category": "编程语言",
    "level": "中级",
    "related_skills": ["React", "Vue", "Node.js"],
    "job_titles": ["前端开发工程师", "全栈开发工程师"],
    "importance": "must"
  }
]
```

### 11.2 初始化脚本
```python
# scripts/init_knowledge_base.py
async def initialize_knowledge_base():
    # 1. 加载职位技能
    skills = load_json("data/job_skills.json")
    await add_to_collection("job_skills", skills)
    
    # 2. 加载面试题
    questions = load_json("data/interview_questions.json")
    await add_to_collection("interview_questions", questions)
    
    # 3. 加载优化经验
    experiences = load_json("data/optimization_experience.json")
    await add_to_collection("optimization_experience", experiences)
    
    print("Knowledge base initialized successfully")
```

---

## 12. 里程碑

| 阶段 | 时间 | 交付内容 |
|------|------|---------|
| M1 | 第1天 | RAG架构设计、知识库schema |
| M2 | 第2天 | ChromaDB集成、检索API |
| M3 | 第3天 | 混合检索实现、重排序 |
| M4 | 第4天 | 前端集成、组件开发 |
| M5 | 第5天 | 数据初始化、测试 |
| M6 | 第6天 | 性能优化、部署文档 |

---

## 13. 风险与对策

| 风险 | 概率 | 影响 | 对策 |
|------|------|------|------|
| 嵌入模型延迟高 | 中 | 高 | 使用本地模型或缓存 |
| 知识库质量差 | 中 | 高 | 人工审核、定期更新 |
| 检索不准确 | 中 | 中 | 混合检索、重排序 |
| 扩展性差 | 低 | 中 | 预留分片机制 |

---

**文档版本**: 1.0.0
**制定日期**: 2026-08-07
**下次评审**: 2026-08-10
