# 会议纪要生成系统

## 项目简介

会议纪要生成系统是一个基于人工智能技术的会议内容自动摘要工具。该系统能够将会议转录文本自动分析并生成结构化的会议纪要，包括会议基本信息、议程、讨论要点、决策事项和后续行动项等内容。

## 功能特点

- **智能摘要**：自动分析会议转录内容，提取关键信息
- **结构化输出**：生成格式统一、条理清晰的会议纪要
- **异步处理**：支持大文件的后台处理，避免长时间等待
- **RESTful API**：提供标准的API接口，便于集成到其他系统
- **实时状态查询**：支持任务状态的实时查询
- **Docker 支持**：提供 Docker 容器化部署方案

## 项目结构

```
.
├── api.py                  # FastAPI后端服务
├── summarizer.py           # Agno API调用封装
├── requirements.txt        # Python依赖包列表
├── Dockerfile              # Docker镜像构建文件
├── docker-compose.yml      # Docker Compose配置文件
├── sample.txt              # 示例会议转录文件
└── test_curl.sh            # API测试脚本
```

## 环境要求

- Python 3.8+
- Agno API 服务（用于AI摘要生成）

## 安装步骤

### 方式一：直接运行

1. 克隆项目代码：
   ```bash
   git clone https://github.com/zhiheng-yu/meeting_summary
   cd meeting_summary
   ```

2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量：
   系统会自动从环境变量中读取 Agno API 服务地址，请确保设置以下环境变量：
   ```bash
   export AGNO_URL="http://localhost:7777"  # Agno API 服务地址
   ```

4. 启动服务：
   ```bash
   python api.py
   ```

### 方式二：Docker 部署

1. 创建 `.env` 文件（可选）：
   ```bash
   echo "AGNO_URL=http://localhost:7777" > .env
   ```

2. 使用 Docker Compose 启动：
   ```bash
   docker-compose up -d
   ```

   或者使用 Docker 直接运行：
   ```bash
   docker build -t meeting-summary .
   docker run -d -p 6001:6001 -e AGNO_URL=http://localhost:7777 meeting-summary
   ```

## 使用方法

### API服务

启动API服务：

```bash
python api.py
```

默认监听端口为6001。

### API接口说明

#### 1. 健康检查
```
GET /health
```

#### 2. 创建会议纪要任务
```
POST /api/summary
```
请求体：
```json
{
  "conversation": "会议转录内容"
}
```

#### 3. 查询任务状态
```
GET /api/tasks/{task_id}
```

#### 4. 获取所有任务列表
```
GET /api/tasks
```

### 测试脚本

项目提供了cURL测试脚本，可直接运行：

```bash
chmod +x test_curl.sh
./test_curl.sh
```
