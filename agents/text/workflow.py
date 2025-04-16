from langgraph.graph import StateGraph

from agents.base_workflow import BaseWorkflow
from agents.text.modules.nodes import PersonaExtractionNode
from agents.text.modules.state import TextState


class TextWorkflow(BaseWorkflow):
    def __init__(self, state: StateGraph):
        super().__init__()
        self.state = state

    def build(self):
        builder = StateGraph(self.state)
        builder.add_node("persona_extraction", PersonaExtractionNode())
        builder.add_edge("__start__", "persona_extraction")
        builder.add_edge("persona_extraction", "__end__")
        # builder.add_conditional_edges(
        #     "call_model",
        #     # call_model 실행이 완료된 후, 다음 노드(들)는
        #     # router의 출력을 기반으로 예약됩니다
        #     router,
        # )
        workflow = builder.compile()
        workflow.name = self.name

        return workflow


text_workflow = TextWorkflow(TextState)
