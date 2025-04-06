from abc import ABC, abstractmethod

from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph


class BaseGraph(ABC):
    """
    본 프로젝트에서 Sub-graph는 각 Agent의 workflow 혹은 pipeline을 구성하는 그래프를 의미합니다.
    해당 클래스는 LangGraph의 StateGraph를 구성하고 컴파일하는 역할을 담당합니다.
    """

    def __init__(self):
        self.graph = self._build_graph()

    @abstractmethod
    def _build_graph(self) -> StateGraph:
        """
        sub graph에 필요한 노드와 엣지를 구성합니다.

        example code:
        ```python
        sub_graph = StateGraph(GraphState)
        sub_graph.add_node("embedder", EmbedderNode())
        sub_graph.add_node("retriever", MongoRetrieverNode())
        sub_graph.add_node("aggregation", MongoAggregationNode())
        sub_graph.add_node("reranker", SimilarityRerankerNode())
        sub_graph.add_conditional_edges("aggregation", some_condition_function, {"yes": "reranker", "no": "embedder"})
        ... # 기타 sub graph 로직
        return sub_graph
        ```
        """
        pass

    def compile(self) -> CompiledStateGraph:
        return self.graph.compile()
