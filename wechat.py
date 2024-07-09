import json
import time

import requests

CORP_ID = "wwa31d0b4728fb094d"
SECRET = "chIdGQHDIqpbPCt4GuTyEA_dlc2dnucs3zQrUrlS_oI"


class WeChatPub:
    s = requests.session()

    def __init__(self):
        self.token = self.get_token()

    def get_token(self):
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={CORP_ID}&corpsecret={SECRET}"
        rep = self.s.get(url)
        if rep.status_code != 200:
            print("request failed.")
            return
        return json.loads(rep.content)["access_token"]

    def send_msg(self, content):
        url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + self.token
        header = {"Content-Type": "application/json"}
        form_data = {
            "touser": "@all",
            "toparty": "StockUpdates",
            "msgtype": "textcard",
            "agentid": 1000002,
            "textcard": {"title": "重整网更新提醒", "description": content, "url": "URL", "btntxt": "更多"},
            "safe": 0,
        }
        rep = self.s.post(url, data=json.dumps(form_data).encode("utf-8"), headers=header)
        if rep.status_code != 200:
            print("request failed.")
            return
        return json.loads(rep.content)


if __name__ == "__main__":
    wechat = WeChatPub()
    timenow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    res = wechat.send_msg(f'<div class="gray">{timenow}</div> <div class="normal">注意！</div><div class="highlight">测试测试！</div>')
    print(res["errmsg"])
