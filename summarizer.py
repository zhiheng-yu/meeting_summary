import os
import requests
from typing import Union


class Summarizer:
    def __init__(self):
        self.agno_url = os.getenv("AGNO_URL", "http://localhost:7777")
        self.agent_id = "summary-agent"

    def meeting_summary(self, conversation: str) -> Union[bool, str]:
        url = f"{self.agno_url}/agents/{self.agent_id}/runs"
        data = {
            'message': conversation,
            'stream': 'false'
        }

        try:
            response = requests.post(url, data=data)
            if response.status_code != 200:
                err_msg = f"远程请求错误, status_code: {response.status_code}, msg: {response.text}"
                return False, err_msg
            content = response.json()["content"]
            return True, content
        except requests.exceptions.RequestException as e:
            err_msg = f"远程请求失败: {str(e)}"
            return False, err_msg


if __name__ == "__main__":
    summarizer = Summarizer()

    with open("./sample.txt", "r") as file:
        conversation = file.read()

    print(summarizer.meeting_summary(conversation))
