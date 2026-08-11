# Bad.md - Job3.0 多Agent协作系统开发错误预警

## 1. LangGraph状态机依赖问题

### 问题描述
缺少langchain和langgraph依赖，导致状态机无法运行。

### 错误信息
```
ModuleNotFoundError: No module named langgraph
```

### 解决方案
在requirements.txt中添加：
```
langchain==0.1.0
langgraph==0.0.15
```

### 预警
- 安装依赖时使用：`pip install -r requirements.txt`
- 确保Python版本 >= 3.8
- 如果遇到版本冲突，尝试安装兼容版本

---

## 2. SSE流式输出依赖

### 问题描述
缺少sse-starlette导致流式API无法工作。

### 错误信息
```
ModuleNotFoundError: No module named sse_starlette
```

### 解决方案
在requirements.txt中添加：
```
sse-starlette==1.8.2
```

### 预警
- 流式输出需要前端支持EventSource
- 确保CORS配置正确
- 注意SSE与WebSocket的区别

---

## 3. 异步函数未正确await

### 问题描述
async函数内部调用其他async函数时忘记使用await。

### 错误信息
```
coroutine object has no attribute
```

### 解决方案
确保所有async函数调用都使用await：
```python
# 错误
result = some_async_function()

# 正确
result = await some_async_function()
```

### 预警
- 在LangGraph节点函数中，所有AI调用都是async的
- 使用async/await确保异步执行
- 避免在async函数中使用time.sleep()，改用asyncio.sleep()

---

## 4. JSON解析失败

### 问题描述
AI返回的内容不是标准JSON格式，导致解析失败。

### 错误信息
```
json.JSONDecodeError
```

### 解决方案
使用正则表达式提取JSON：
```python
def parse_json_response(response: str) -> dict:
    try:
        return json.loads(response)
    except:
        import re
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        return {"raw": response}
```

### 预警
- AI模型可能返回带markdown格式的JSON
- 某些模型会添加解释性文本
- 使用健壮的解析器处理边界情况

---

## 5. 迭代死循环

### 问题描述
CriticAgent持续返回NEEDS_IMPROVEMENT，导致无限循环。

### 解决方案
设置硬性终止条件：
```python
MAX_ITERATIONS = 5  # 最多迭代5轮
CONVERGENCE_PATIENCE = 2  # 连续2轮改进小于5%则收敛
```

### 预警
- 在状态机中添加最大迭代次数限制
- 监控改进幅度，改进过小时提前收敛
- 设置合理的目标分数阈值

---

## 6. 状态丢失

### 问题描述
前端断连后，后端仍在执行，但前端无法获取结果。

### 解决方案
使用LangGraph的检查点机制：
```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("cache/checkpoints.db")
graph = StateGraph(AgentState, checkpointer=checkpointer)
```

### 预警
- 使用thread_id关联前端会话和后端执行
- 前端重连时从checkpoint恢复状态
- 定期清理过期checkpoint

---

## 7. Token超出限制

### 问题描述
长简历+长JD超出LLM的上下文窗口限制。

### 错误信息
```
RateLimitError: This model maximum context window is 8192 tokens
```

### 解决方案
1. 截断输入：
```python
resume_text = resume_text[:4000]  # 限制长度
jd_text = jd_text[:2000]
```

2. 使用摘要：
```python
summary = await summarize_long_text(full_text)
```

### 预警
- 不同模型的上下文窗口不同
- GPT-4通常有8K/16K/32K token
- DeepSeek通常有8K/32K/128K token
- 保留关键信息，截断次要内容

---

## 8. API超时

### 问题描述
AI API调用超时，导致节点失败。

### 错误信息
```
TimeoutError
httpx.ReadTimeout
```

### 解决方案
1. 设置合理的超时时间：
```python
async with httpx.AsyncClient(timeout=180.0) as client:
    ...
```

2. 实现重试机制：
```python
for attempt in range(3):
    try:
        response = await call_api()
        break
    except TimeoutError:
        if attempt == 2:
            raise
        await asyncio.sleep(2 ** attempt)  # 指数退避
```

### 预警
- 设置合理的超时时间（建议60-180秒）
- 使用指数退避重试
- 降级到简单模式作为后备

---

## 9. PowerShell编码问题

### 问题描述
Windows PowerShell无法正确处理UTF-8编码的中文字符。

### 错误信息
```
UnicodeEncodeError: gbk codec cant encode character
```

### 解决方案
1. 创建Python脚本文件而非直接在PowerShell中写入
2. 使用Python的UTF-8 BOM编码
3. 避免在Python代码中使用emoji

### 预警
- Windows控制台默认使用GBK编码
- Python文件应保存为UTF-8 BOM编码
- 避免在代码中使用emoji和特殊字符

---

## 10. Vue组件字符串未转义

### 问题描述
Vue文件中多行字符串使用实际换行符而非转义字符。

### 错误信息
```
[vue/compiler-sfc] Unterminated string constant
```

### 解决方案
使用反引号（模板字符串）或将换行替换为\n：
```vue
content: `第一行
第二行`

<!-- 或 -->
content: "第一行\n第二行"
```

### 预警
- Vue模板字符串应使用反引号
- 避免使用单引号或双引号包裹多行字符串
- 修改文件后注意检查编码

---

## 11. CORS配置问题

### 问题描述
前端无法调用后端API，跨域请求被阻止。

### 错误信息
```
Access to XMLHttpRequest at from origin has been blocked by CORS policy
```

### 解决方案
在FastAPI中配置CORS：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 预警
- 开发环境允许localhost
- 生产环境限制具体域名
- 注意credentials和origins的组合

---

## 12. 依赖安装顺序

### 问题描述
pip安装顺序导致版本冲突。

### 错误信息
```
ERROR: Cannot install langchain==0.1.0 because these package versions have conflicting dependencies.
```

### 解决方案
1. 使用虚拟环境
2. 按特定顺序安装：
```bash
pip install fastapi uvicorn
pip install langchain langgraph
pip install -r requirements.txt
```

### 预警
- 始终使用虚拟环境
- requirements.txt中明确定义版本
- 安装前清理旧版本

---

## 13. 错误处理策略

### 最佳实践
1. **降级模式**：完整流程失败时降级到简单模式
2. **容错机制**：单个Agent失败不影响整体流程
3. **日志记录**：记录所有错误便于排查
4. **用户提示**：友好地展示错误信息

### 实现示例
```python
try:
    result = await run_optimization(...)
    return result
except APITimeoutError:
    logger.warning("API timeout, falling back to simple mode")
    return await run_simple_optimization(...)
except Exception as e:
    logger.error(f"Optimization failed: {e}")
    return {
        "status": "failed",
        "error": str(e),
        "fallback_mode": True
    }
```

---

**创建时间**: 2026-08-07
**最后更新**: 2026-08-07
**版本**: 1.0.0
