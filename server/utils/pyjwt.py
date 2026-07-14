import jwt
import time
import config
from typing import Optional
from fastapi import Header
from model.result_model import ResponseModel

class JWT:
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }

    def create(self, payload: dict,  expire: int = 60*60*5):
        payload["exp"] = int(time.time()) + expire
        return jwt.encode(payload, algorithm="HS256", headers=self.headers, key=config.JWT_SECRET)

    def decode(self, token: str):
        try:
            return jwt.decode(token, key=config.JWT_SECRET, algorithms=["HS256"])
        except:
            return

    def check(self, token: Optional[str] = Header("")):
        payload = self.decode(token)
        if payload:
            if payload["exp"] > int(time.time()) and (payload["device_id"] in config.DEVICE_WHITELIST or "*" in config.DEVICE_WHITELIST):
                return payload
            else:
                return ResponseModel(code="40102", message="Token过期")
        return ResponseModel(code="40101", message="Token无效")

