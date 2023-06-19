from abc import ABC, abstractmethod
import langchain
from typing import List


class AgentMemoryInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def save_messages(
        self,
        name: str,
        topic: str,
        messages: List[str],
        roles: List[str],
    ):
        pass


class AgentMemoryBase(AgentMemoryInterface):
    def __init__(self):
        super().__init__()
    
    def save_messages(
        self,
        name: str,
        topic: str,
        messages: List[str],
        roles: List[str],
    ):
        pass