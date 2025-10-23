# 会议纪要生成系统

## 项目简介

会议纪要生成系统是一个基于人工智能技术的会议内容自动摘要工具。该系统能够将会议转录文本自动分析并生成结构化的会议纪要，包括会议基本信息、议程、讨论要点、决策事项和后续行动项等内容。

## 功能特点

- **智能摘要**：自动分析会议转录内容，提取关键信息
- **结构化输出**：生成格式统一、条理清晰的会议纪要
- **异步处理**：支持大文件的后台处理，避免长时间等待
- **思考过程可视化**：可选显示AI的推理思考过程
- **RESTful API**：提供标准的API接口，便于集成到其他系统
- **实时状态查询**：支持任务状态的实时查询

## 项目结构

```
.
├── api.py                  # FastAPI后端服务
├── main.py                 # 命令行版本主程序
├── summary_agent.py        # AI代理核心逻辑
├── config/                 # 配置文件目录
│   ├── summary_prompt.md   # AI提示词模板
│   └── minutes_format.md   # 会议纪要格式模板
├── requirements.txt        # Python依赖包列表
├── sample.txt              # 示例会议转录文件
└── test_curl.sh            # API测试脚本
```

## 环境要求

- Python 3.8+
- OpenAI API 兼容接口及密钥

## 安装步骤

1. 克隆项目代码：
   ```bash
   git clone https://github.com/zhiheng-yu/meeting_summary
   cd meeting_summary
   ```

2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置API密钥：
   系统会自动从环境变量中读取API密钥和基础URL，请确保设置以下环境变量：
   ```bash
   export OPENAI_API_KEY="your-api-key"
   export OPENAI_BASE_URL="your-openai-api-compatible-url"  # 可选，默认为 https://api.openai.com/v1
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
GET /
```

#### 2. 创建会议纪要任务
```
POST /api/summary
```
请求体：
```json
{
  "conversation": "会议转录内容",
  "thinking": true
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

## 配置说明

### AI提示词模板 (`config/summary_prompt.md`)

定义了AI代理的角色、技能、规则、工作流程和输出格式等。

### 会议纪要格式模板 (`config/minutes_format.md`)

定义了生成会议纪要的标准格式结构。

## 输出示例

生成的会议纪要包含以下主要部分：

1. **基本信息**：会议日期、时间、参会人员等
2. **会议议程**：会议的主要议题列表
3. **讨论要点**：各议题的详细讨论内容
4. **行动项**：需要跟进的任务、负责人和截止时间
