from typing import Annotated, Dict, List, TypedDict, Union

from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    query: str
    image: str
    chat_history: List[Dict[str, str]]
    hypothetical_doc: str
    embedding: List[float]
    documents: List[Dict]
    reranked_documents: List[Dict]
    aggregated_documents: List[Dict]
    popularity_ranked_documents: List[Dict]
    scoring_info: Dict[str, Union[float, Dict]]
    judge_answer: Annotated[list, add_messages]
    response: Annotated[list, add_messages]
