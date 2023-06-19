from enum import Enum
import os


class AgentMemoryMode(Enum):
    AGENT_MEMORY_MODE_NONE = "AGENT_MEMORY_MODE_NONE"
    AGENT_MEMORY_MODE_SQLITE = "AGENT_MEMORY_MODE_SQLITE"


def get_agent_memory(
    agent_memory_mode: AgentMemoryMode = AgentMemoryMode.AGENT_MEMORY_MODE_NONE,
    memory_path: str = "ckpt/agent_memory",
    **kwargs,
):
    from .base import AgentMemoryBase
    from .sqlite import AgentMemorySQLite

    return {
        AgentMemoryMode.AGENT_MEMORY_MODE_NONE: AgentMemoryBase(),
        AgentMemoryMode.AGENT_MEMORY_MODE_SQLITE: AgentMemorySQLite(
            db_path=os.path.join(memory_path, "memory.db"),
        ),
    }.get(agent_memory_mode)
