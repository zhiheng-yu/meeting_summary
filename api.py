from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json

from summarizer import Summarizer
from counselor import Counselor


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

@app.get("/")
def root():
    return {"message": "AI Meeting Summary API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Meeting Summary API"}

@app.post("/summary")
def create_meeting_summary(conversation: str = Form(...)):
    """生成会议纪要"""
    if not conversation or not conversation.strip():
        raise HTTPException(status_code=400, detail="会议转录内容不能为空")

    summarizer = Summarizer()
    success, content = summarizer.meeting_summary(conversation)

    return {"success": success, "content": content}

@app.post("/knowledge")
def upload_knowledge(meeting_id: str = Form(...), conversation: str = Form(...), timeout: int = Form(10)):
    """上传知识到知识库"""
    if not meeting_id or not meeting_id.strip():
        raise HTTPException(status_code=400, detail="会议ID不能为空")
    if not conversation or not conversation.strip():
        raise HTTPException(status_code=400, detail="会议转录内容不能为空")

    counselor = Counselor()
    success, result = counselor.upload_knowledge(meeting_id, conversation, timeout)

    if not success:
        raise HTTPException(status_code=500, detail=result)

    return {"success": True, "message": result}

@app.post("/counsel")
def counsel(meeting_id: str = Form(...), message: str = Form(...)):
    """咨询（流式响应）"""
    if not meeting_id or not meeting_id.strip():
        raise HTTPException(status_code=400, detail="会议ID不能为空")
    if not message or not message.strip():
        raise HTTPException(status_code=400, detail="咨询内容不能为空")

    counselor = Counselor()

    def generate():
        try:
            for content, reason_content, status in counselor.counsel(meeting_id, message):
                # 使用 SSE 格式返回流式数据
                json_data = {
                    "content": content,
                    "reason_content": reason_content,
                    "status": status
                }
                yield f"data: {json.dumps(json_data, ensure_ascii=False)}\n\n"
        except Exception as e:
            json_data = {
                "error": str(e)
            }
            yield f"data: {json.dumps(json_data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/history/{meeting_id}")
def get_history(meeting_id: str):
    """查询历史信息"""
    if not meeting_id or not meeting_id.strip():
        raise HTTPException(status_code=400, detail="会议ID不能为空")

    counselor = Counselor()
    success, history, message = counselor.get_history(meeting_id)

    return {"success": success, "history": history, "message": message}

@app.delete("/history/{meeting_id}")
def delete_history(meeting_id: str):
    """删除历史信息"""
    if not meeting_id or not meeting_id.strip():
        raise HTTPException(status_code=400, detail="会议ID不能为空")

    counselor = Counselor()
    success, message = counselor.clean_history(meeting_id)

    return {"success": success, "message": message}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=6001, reload=True)
