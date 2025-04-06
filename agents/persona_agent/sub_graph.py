from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agents.base_sub_graph import BaseSubGraph
from agents.graph_state import GraphState
from agents.persona_agent.nodes import PersonaExtractionNode


class PersonaSubGraph(BaseSubGraph):
    """
    본 프로젝트에서 Sub-graph는 각 Agent의 workflow 혹은 pipeline을 구성하는 그래프를 의미합니다.
    해당 클래스는 LangGraph의 StateGraph를 구성하고 컴파일하는 역할을 담당합니다.
    """

    def __init__(self):
        self.graph = self._build_sub_graph()

    def _build_sub_graph(self):
        sub_graph = StateGraph(GraphState)
        sub_graph.add_node("persona_extraction", PersonaExtractionNode())
        sub_graph.add_edge(START, "persona_extraction")
        sub_graph.add_edge("persona_extraction", END)
        return sub_graph

    def compile(self) -> CompiledStateGraph:
        return self.graph.compile()
