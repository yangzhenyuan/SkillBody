""" 消息系统 """

from typing import Any, Dict, Literal

from pydantic import BaseModel


MessageRole = Literal["system", "user", "assistant", "tool"]

class Message(BaseModel):

    content: str
    role: MessageRole

    def __init__(self, content: str, role: MessageRole):
        super().__init__(
            content=content,
            role=role
        )

    def to_dict(self) -> Dict[str, Any]:
        """ 转换为字典格式 """
        return {
            "role": self.role,
            "content": self.content
        }
    
    def __str__(self) -> str:
        return f"[{self.role}] {self.content}"