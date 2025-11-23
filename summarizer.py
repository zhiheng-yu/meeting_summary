import os
import requests


class Summarizer:
    def __init__(self):
        self.agno_url = os.getenv("AGNO_URL", "http://localhost:7777")
        self.agent_id = "summary-agent"

    def meeting_summary(self, conversation):
        """
        调用 Agno API 生成会议纪要

        Args:
            conversation: 会议转录内容

        Returns:
            str: 会议纪要内容
        """
        url = f"{self.agno_url}/agents/{self.agent_id}/runs"

        # 准备 form-data
        data = {
            'message': conversation,
            'stream': 'false'
        }

        try:
            # 发送 POST 请求
            response = requests.post(url, data=data)
            response.raise_for_status()  # 如果状态码不是 200，抛出异常

            # 返回 JSON 响应
            return response.json()["content"]
        except requests.exceptions.RequestException as e:
            # 处理请求异常
            raise Exception(f"请求 Agno API 时发生错误: {str(e)}")


if __name__ == "__main__":
    with open("./sample.txt", "r") as file:
        conversation = file.read()
    summarizer = Summarizer()
    print(summarizer.meeting_summary(conversation))
