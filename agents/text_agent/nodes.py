from agents.base_node import BaseNode
from agents.graph_state import GraphState
from agents.manager_agent.chain import Chain


class TextNode(BaseNode):
    """가상의 문서를 생성하는 노드"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "Single2HyDENode"
        self.chain = Chain.set_hyde_chain(mode="single")

    def process(self, state: GraphState) -> GraphState:
        hypothetical_doc = self.chain.invoke({"query": state["query"]})
        return {"hypothetical_doc": hypothetical_doc}
