""" Agent的基类 """

from abc import ABC, abstractmethod
from typing import List, Optional

from core.agent_client import AgentClient
from core.config import Config
from core.message import Message


class Agent(ABC):
    def __init__(
            self,
            llm: AgentClient,
            prompt: Optional[str] = None,
            config: Optional[Config] = None
        ):
        self.llm = llm
        self.prompt = prompt
        self.config = config
        self.history: List[Message] = []

    @abstractmethod
    def run(self, input: str, **kwargs) -> str:
        """ agent执行的入口：运行agent """
        pass
