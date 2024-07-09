import json

import requests


class WeBot:
    webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=f45c82e7-4fff-4d9c-bc08-e3f4a168e43b"

    # 发送文本消息
    def send_text(self, content):

        header = {
            "Content-Type": "application/json",
            "Charset": "UTF-8",
        }

        data = {
            "msgtype": "text",
            "text": {
                "content": content,
            },
        }
        data = json.dumps(data)
        try:
            requests.post(url=self.webhook, data=data, headers=header)
        except Exception as e:
            print(f"request failed: {e}")

    # 发送markdown消息
    def send_md(self, content):
        header = {"Content-Type": "application/json", "Charset": "UTF-8"}
        data = {"msgtype": "markdown", "markdown": {"content": content}}
        data = json.dumps(data)
        requests.post(url=self.webhook, data=data, headers=header)


if __name__ == "__main__":
    bot = WeBot()
    bot.send_text(content="Tesing")
