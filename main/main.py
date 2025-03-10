from quart import Quart, request
import asyncio
from typing import Optional, Dict, Any
import aiohttp
import requests

_TYPE = 1
# 文本消息
_NAME = "全球票房"
_DESCRIPTION = "全球票房"
_TARGET = "票房"

app = Quart(__name__)

class Piaofang:
    def __init__(self, message, fromid):
        self.name = message[2:]
        self.fromid = fromid

    async def reply(self, url: str, method: str = "GET", params: Optional[Dict[str, str]] = None,
                  data: Optional[Any] = None, json: Optional[Dict] = None,
                  headers: Optional[Dict[str, str]] = None, retry: int = 3, ssl: bool = True, timeout: float = 10,
                  backoff_factor: float = 0.5) -> Any:
        timeout = aiohttp.ClientTimeout(total=timeout)
        for attempt in range(retry):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    request_method = getattr(session, method.lower(), session.get)
                    async with request_method(url=url, params=params, data=data, json=json, headers=headers,
                                              ssl=ssl) as response:
                        response.raise_for_status()
                        content_type = response.headers.get('Content-Type', '')
                        if 'application/json' in content_type:
                            return await response.json()
                        else:
                            return await response.text()
            except aiohttp.ClientError as e:
                if attempt + 1 == retry:
                    raise
                else:
                    await asyncio.sleep(backoff_factor * (2 ** attempt))

    async def send_text(self, msg):
        data = {
            "method": "sendText",
            "wxid": self.fromid,
            "msg": msg,
            "atid": "",
            "pid": 0
        }
        reply = await self.reply("http://127.0.0.1:8203/api?json&key=D60FFF4BF40769AA3113D11918352BDAFA4C3936", method='POST',
                        json=data)
        print(reply)

    async def query(self):
        url = 'https://api.mhimg.cn/api/Box_office'
        try:
            reply = requests.get(url).text
            msg = str(reply)
            await self.send_text(msg)
        except Exception as e:
            print(e)

# POST 请求示例
@app.route('/', methods=['POST'])
async def duanju():
    message = await request.get_json()
    msg = message["data"].get("msg", "")
    fromid = message["data"].get("fromid", "")
    if msg[:2] == _TARGET:
        piaofang = Piaofang(msg, fromid)
        await piaofang.query()
        return {"status": "success"}
    else:
        return {"status": "error", "message": "Target not found."}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10099)
