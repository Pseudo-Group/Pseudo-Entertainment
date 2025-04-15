from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class TextState(TypedDict):
    content_topic: str
    content_type: str
    query: str
    response: Annotated[list, add_messages]
