import os

from summary_agent import OpenAIAgent

if __name__ == '__main__':
    file_path = input("选择需要总结的会议转录文件: ")
    file_name, file_format = os.path.splitext(file_path)

    with open(file_path, "r", encoding='utf-8') as f:
        conversation = f.read()

    agent = OpenAIAgent()
    response = agent.meeting_summary(conversation)
    if response["thinking"]:
        print("Thinking:")
        print(response["reasoning_content"])
        print("--------------------------------")

    print(response["content"])
    meeting_minutes = response["content"]

    with open(file_name + "_summary.md", "w", encoding='utf-8') as f:
        f.write(meeting_minutes)
