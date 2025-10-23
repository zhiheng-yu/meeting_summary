#!/bin/bash

# AI Meeting Summary API 异步轮询模式 cURL 测试脚本

API_BASE_URL="http://localhost:6001"

echo "🚀 AI Meeting Summary API 异步轮询模式 cURL 测试"
echo "=============================================="

# 测试健康检查
echo "1. 测试健康检查..."
curl -s -X GET "$API_BASE_URL/health" | jq .
echo ""

# 测试模型信息
echo "2. 测试模型信息..."
curl -s -X GET "$API_BASE_URL/api/models" | jq .
echo ""

# 创建会议纪要任务
echo "3. 创建会议纪要任务..."

# 从 sample.txt 文件读取会议转录内容
TRANSCRIPTION_FILE="./sample.txt"

if [ ! -f "$TRANSCRIPTION_FILE" ]; then
    echo "❌ 错误: 找不到转录文件 $TRANSCRIPTION_FILE"
    exit 1
fi

# 使用 jq 安全地从文件创建 JSON 请求体
TASK_RESPONSE=$(curl -s -X POST "$API_BASE_URL/api/summary" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --rawfile conversation "$TRANSCRIPTION_FILE" '{"conversation": $conversation, "thinking": true}')")

echo "任务创建响应:"
echo "$TASK_RESPONSE" | jq .
echo ""

# 提取任务ID
TASK_ID=$(echo "$TASK_RESPONSE" | jq -r '.task_id')

if [ "$TASK_ID" = "null" ] || [ -z "$TASK_ID" ]; then
    echo "❌ 任务创建失败，无法获取任务ID"
    exit 1
fi

echo "✅ 任务创建成功，任务ID: $TASK_ID"
echo ""

# 轮询任务状态
echo "4. 开始轮询任务状态..."
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    echo "尝试 $ATTEMPT/$MAX_ATTEMPTS..."

    STATUS_RESPONSE=$(curl -s -X GET "$API_BASE_URL/api/tasks/$TASK_ID")

    STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')
    MESSAGE=$(echo "$STATUS_RESPONSE" | jq -r '.message')

    echo "状态: $STATUS"
    echo "消息: $MESSAGE"

    if [ "$STATUS" = "completed" ]; then
        echo "🎉 任务完成！"
        echo ""
        echo "最终结果:"
        echo "$STATUS_RESPONSE" | jq .
        break
    elif [ "$STATUS" = "failed" ]; then
        echo "❌ 任务失败！"
        ERROR=$(echo "$STATUS_RESPONSE" | jq -r '.error')
        echo "错误信息: $ERROR"
        break
    else
        echo "⏳ 任务进行中，等待 5 秒后重试..."
        sleep 5
    fi
    echo ""
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "⏰ 轮询超时"
fi

echo ""
echo "5. 测试任务列表..."
curl -s -X GET "$API_BASE_URL/api/tasks" | jq .
echo ""

echo "=============================================="
echo "🎉 cURL 测试完成！"
