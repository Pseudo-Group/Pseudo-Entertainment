from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class MainState(TypedDict):
    content_topic: str
    content_type: str
    query: str
    image: str
    response: Annotated[list, add_messages]
