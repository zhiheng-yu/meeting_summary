# 会议纪要生成系统

## 项目简介

会议纪要生成系统是一个基于人工智能技术的会议内容自动摘要和知识管理工具。该系统能够将会议转录文本自动分析并生成结构化的会议纪要，同时支持将会议内容上传到知识库，并提供基于知识库的智能咨询功能。

## 功能特点

- **智能摘要**：自动分析会议转录内容，提取关键信息并生成结构化会议纪要
- **知识库管理**：支持将会议转录内容上传到知识库，便于后续查询和分析
- **智能咨询**：基于知识库内容提供流式响应的智能咨询功能
- **会话历史**：支持查询和删除特定会议的历史对话记录
- **RESTful API**：提供标准的API接口，便于集成到其他系统
- **流式响应**：咨询接口支持 Server-Sent Events (SSE) 流式输出
- **Docker 支持**：提供 Docker 容器化部署方案

## 环境要求

- Python 3.8+
- Agno API 服务（用于AI摘要生成）

## 依赖服务

[meeting-agents（基于 Agno 框架构建的会议智能体）](https://github.com/zhiheng-yu/meeting-agents)

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

1. 创建 `.env` 文件：
   ```bash
   echo "AGNO_URL=http://localhost:7777" > .env
   ```

2. 构建 Docker 镜像：
   ```bash
   docker build -t meeting-assistant .
   ```

3. 使用 Docker Compose 启动：
   ```bash
   docker-compose up -d
   ```

   或者使用 Docker 直接运行：
   ```bash
   docker run -d -p 6001:6001 -e AGNO_URL=http://localhost:7777 meeting-assistant
   ```

### 接口使用方法

[会议助手接口文档-Apifox](https://s.apifox.cn/b06653a0-ec1a-41a5-8890-f5e9f9672f60)
