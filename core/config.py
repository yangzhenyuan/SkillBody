""" agent配置类 """

import os
from typing import Optional

from pydantic import BaseModel


class Config(BaseModel):

    # LLM配置
    temperature: float = 0.7
    max_token: Optional[int] = None

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            temperature = float(os.getenv("TEMPERATURE", "0.7")),
            max_token = int(os.getenv("MAX_TOKEN")) if os.getenv("MAX_TOKEN") else None
        )