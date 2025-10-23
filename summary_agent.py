import os
from openai import OpenAI


class SummaryAgent:
    def __init__(self, thinking=True):
        local_dir = os.path.dirname(__file__)
        minutes_format_path = os.path.join(local_dir, "config", "minutes_format.md")
        with open(minutes_format_path, "r", encoding='utf-8') as f:
            self.minutes_format = f.read()

        system_prompt_path = os.path.join(local_dir, "config", "summary_prompt.md")
        with open(system_prompt_path, "r", encoding='utf-8') as f:
            self.system_prompt = f.read()

        self.system_prompt = self.system_prompt.replace("{{minutes_format}}", self.minutes_format)

        self.thinking = thinking

    def generate(self, messages):
        raise NotImplementedError

    def meeting_summary(self, conversation):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": conversation},
        ]

        return self.generate(messages)


class OpenAIAgent(SummaryAgent):
    def __init__(self, thinking=True):
        super().__init__(thinking)
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )

    def generate(self, messages):
        self.last_reasoning_content = ""
        self.last_content = ""

        response = self.client.chat.completions.create(
            model="qwen3-30b-a3b-thinking-2507",
            messages=messages,
            stream=False
        )

        # 提取回复内容
        if response.choices and len(response.choices) > 0:
            if self.thinking:
                return { "thinking": True,
                         "reasoning_content": response.choices[0].message.reasoning_content,
                         "content": response.choices[0].message.content }
            else:
                return { "thinking": False,
                         "content": response.choices[0].message.content }
        else:
            return { "thinking": False, "content": "" }
