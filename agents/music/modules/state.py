from typing import Annotated, Dict, List, TypedDict

from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    content_topic: str
    content_type: str
    query: str
    chat_history: List[Dict[str, str]]
    documents: List[Dict]
    response: Annotated[list, add_messages]
