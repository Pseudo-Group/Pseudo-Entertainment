from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from agents.base_sub_graph import BaseSubGraph
from agents.graph_state import GraphState


class ManangerSubGraph(BaseSubGraph):
    """
    본 프로젝트에서 Sub-graph는 각 Agent의 workflow 혹은 pipeline을 구성하는 그래프를 의미합니다.
    해당 클래스는 LangGraph의 StateGraph를 구성하고 컴파일하는 역할을 담당합니다.
    """

    def __init__(self):
        self.graph = self._build_sub_graph()

    def _build_sub_graph(self):
        sub_graph = StateGraph(GraphState)
        # TODO: Manager Agent 역할에 맞춰서 Chain 및 Node 추가
        return sub_graph

    def compile(self) -> CompiledStateGraph:
        return self.graph.compile()
