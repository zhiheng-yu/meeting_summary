from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor

from summarizer import Summarizer


app = FastAPI(
    title="AI Meeting Summary API",
    description="基于 AI 的会议纪要生成服务",
    version="1.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 任务状态枚举
class TaskStatus(str, Enum):
    PENDING = "pending"      # 等待中
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"        # 失败

# 任务存储（生产环境建议使用 Redis 或数据库）
task_storage: Dict[str, Dict[str, Any]] = {}

# 请求模型
class MeetingSummaryRequest(BaseModel):
    conversation: str

# 任务创建响应模型
class TaskCreateResponse(BaseModel):
    task_id: str
    status: TaskStatus
    message: str
    created_at: datetime

# 任务状态响应模型
class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    progress: Optional[int] = None
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# 后台任务处理函数
async def process_meeting_summary(task_id: str, conversation: str):
    """后台处理会议纪要生成任务"""
    try:
        # 更新任务状态为处理中
        task_storage[task_id]["status"] = TaskStatus.PROCESSING
        task_storage[task_id]["updated_at"] = datetime.now()
        task_storage[task_id]["message"] = "正在生成会议纪要..."

        # 初始化 AI 代理
        summarizer = Summarizer()

        # 使用线程池执行阻塞的AI调用
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                summarizer.meeting_summary,
                conversation
            )

        # 更新任务状态为完成
        task_storage[task_id]["status"] = TaskStatus.COMPLETED
        task_storage[task_id]["updated_at"] = datetime.now()
        task_storage[task_id]["message"] = "会议纪要生成完成"
        task_storage[task_id]["result"] = {
            "success": True,
            "content": result
        }

    except Exception as e:
        # 更新任务状态为失败
        task_storage[task_id]["status"] = TaskStatus.FAILED
        task_storage[task_id]["updated_at"] = datetime.now()
        task_storage[task_id]["message"] = "会议纪要生成失败"
        task_storage[task_id]["error"] = str(e)

# 健康检查端点
@app.get("/")
async def root():
    return {"message": "AI Meeting Summary API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Meeting Summary API"}

# 创建会议纪要生成任务
@app.post("/api/summary", response_model=TaskCreateResponse)
async def create_meeting_summary_task(request: MeetingSummaryRequest, background_tasks: BackgroundTasks):
    """创建会议纪要生成任务"""
    try:
        # 验证输入
        if not request.conversation or not request.conversation.strip():
            raise HTTPException(
                status_code=400,
                detail="会议转录内容不能为空"
            )

        # 生成任务ID
        task_id = str(uuid.uuid4())
        current_time = datetime.now()

        # 创建任务记录
        task_storage[task_id] = {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "conversation": request.conversation,
            "created_at": current_time,
            "updated_at": current_time,
            "message": "任务已创建，等待处理",
            "result": None,
            "error": None
        }

        # 添加后台任务
        background_tasks.add_task(
            process_meeting_summary,
            task_id,
            request.conversation
        )

        return TaskCreateResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="任务已创建，请使用任务ID查询状态",
            created_at=current_time
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建任务时发生错误: {str(e)}"
        )

# 查询任务状态
@app.get("/api/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """查询任务状态（非阻塞，立即返回当前状态）"""
    if task_id not in task_storage:
        raise HTTPException(
            status_code=404,
            detail="任务不存在"
        )

    # 立即返回任务的当前状态，不等待任务完成
    task = task_storage[task_id]
    return TaskStatusResponse(
        task_id=task["task_id"],
        status=task["status"],
        message=task["message"],
        created_at=task["created_at"],
        updated_at=task["updated_at"],
        result=task["result"],
        error=task["error"]
    )

# 获取所有任务列表（可选，用于调试）
@app.get("/api/tasks")
async def list_tasks():
    """获取所有任务列表"""
    return {
        "tasks": [
            {
                "task_id": task["task_id"],
                "status": task["status"],
                "created_at": task["created_at"],
                "updated_at": task["updated_at"]
            }
            for task in task_storage.values()
        ],
        "total": len(task_storage)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6001)
