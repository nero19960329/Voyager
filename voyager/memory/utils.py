import langchain


def get_message_role(
    message: langchain.schema.BaseMessage,
) -> str:
    if isinstance(message, langchain.schema.SystemMessage):
        return "system"
    elif isinstance(message, langchain.schema.HumanMessage):
        return "human"
    elif isinstance(message, langchain.schema.AIMessage):
        return "ai"
    return None
