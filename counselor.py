import os
import requests
import json
import time
from typing import Generator, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Counselor:
    def __init__(self):
        self.agno_url = os.getenv("AGNO_URL", "http://localhost:7777")
        self.agent_id = "counselor-agent"

    def get_knowledge_status(self, content_id: str) -> Union[bool, str]:
        """查询知识库内容的状态"""
        url = f"{self.agno_url}/knowledge/content/{content_id}"
        response = requests.get(url)
        if response.status_code != 200:
            err_msg = f"远程请求错误, status_code: {response.status_code}, msg: {response.text}"
            return False, err_msg
        return True, response.json().get("status")

    def upload_knowledge(self, meeting_id: str, conversation: str, timeout: int = 10) -> Union[bool, str]:
        # 发送上传知识请求
        url = f"{self.agno_url}/knowledge/content"
        params = {"db_id": "meeting_kb"}
        data = {
            "name": f"meeting_transcripts_{meeting_id}",
            "metadata": json.dumps({"meeting_id": meeting_id}),
            "text_content": conversation
        }
        response = requests.post(url, params=params, data=data)
        if response.status_code != 202:
            err_msg = f"远程请求错误, status_code: {response.status_code}, msg: {response.text}"
            return False, err_msg
        result = response.json()
        content_id = result.get("id")

        # 查询知识处理状态，等待完成或超时
        start_time = time.time()
        poll_interval = 0.5

        while True:
            success, status = self.get_knowledge_status(content_id)
            if not success:
                return False, status

            if status == "completed":
                return True, "success"
            elif status == "failed":
                return False, "failed"
            else:
                elapsed_time = time.time() - start_time
                if elapsed_time >= timeout:
                    return False, "timeout"
                time.sleep(poll_interval)

    def counsel(self, meeting_id: str, message: str) -> Generator[str, None, None]:
        url = f"{self.agno_url}/agents/{self.agent_id}/runs"
        query_with_filters = f"{message}\n\nSearch knowledge with filters: meeting_id={meeting_id}"
        data = {
            'message': query_with_filters,
            'stream': 'true',
            'session_id': meeting_id
        }

        try:
            response = requests.post(url, data=data, stream=True)
            response.raise_for_status()

            # 解析 SSE 流式响应
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue

                # SSE 格式：data: {...}
                if line.startswith("data: "):
                    try:
                        json_str = line[6:]  # 移除 "data: " 前缀
                        event_data = json.loads(json_str)
                        event = event_data.get("event", "")
                        reason_content = event_data.get("reasoning_content", "")
                        content = event_data.get("content", "")
                        if event == "ToolCallCompleted":
                            logger.info(f"ToolCallCompleted: {content}")
                        elif event == "RunContent" and reason_content:
                            yield "", reason_content, "thinking"
                        elif event == "RunContent" and content:
                            yield content, "", "end"
                    except json.JSONDecodeError:
                        pass
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求 Agno API 时发生错误: {str(e)}")

    def get_history(self, meeting_id: str) -> Union[bool, list[dict], str]:
        url = f"{self.agno_url}/sessions/{meeting_id}"

        try:
            response = requests.get(url)
            if response.status_code != 200:
                err_msg = f"远程请求错误, status_code: {response.status_code}, msg: {response.text}"
                return False, [], err_msg

            historys = response.json().get("chat_history", [])
            filtered_historys = []
            for history in historys:
                role = history.get("role", "")
                content = history.get("content", "")
                if role == "user" and content:
                    original_content = content.replace(
                        f"\n\nSearch knowledge with filters: meeting_id={meeting_id}", "")
                    filtered_historys.append({"role": "user", "content": original_content})
                elif role == "assistant" and content:
                    filtered_historys.append({"role": "assistant", "content": content})
            return True, filtered_historys, "success"
        except requests.exceptions.RequestException as e:
            err_msg = f"远程请求失败: {str(e)}"
            return False, [], err_msg

    def clean_history(self, meeting_id: str) -> Union[bool, str]:
        url = f"{self.agno_url}/sessions/{meeting_id}"

        try:
            response = requests.delete(url)
            if response.status_code != 204:
                err_msg = f"远程请求错误, status_code: {response.status_code}, msg: {response.text}"
                return False, err_msg
            return True, "success"
        except requests.exceptions.RequestException as e:
            err_msg = f"远程请求失败: {str(e)}"
            return False, err_msg


if __name__ == "__main__":
    counselor = Counselor()
    meeting_id = "123"

    with open("./sample.txt", "r") as file:
        conversation = file.read()
    result = counselor.upload_knowledge(meeting_id, conversation)
    print(result)

    for content in counselor.counsel(meeting_id, "会议的主题是什么？"):
        print(content, end="", flush=True)
    print("")

    print(counselor.get_history(meeting_id))
    counselor.clean_history(meeting_id)
    print(counselor.get_history(meeting_id))
