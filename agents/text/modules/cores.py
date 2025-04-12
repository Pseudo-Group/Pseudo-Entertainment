from agents.base_node import BaseNode
from agents.text.modules.chains import PersonaChain
from agents.text.modules.state import GraphState


class PersonaExtractionNode(BaseNode):
    """콘텐츠 종류에 적합한 페르소나를 추출하는 노드"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = self.__class__.__name__
        self.chain = PersonaChain.set_extraction_chain()

    def process(self, state: GraphState) -> GraphState:
        extracted_persona = self.chain.invoke(
            {
                "content_topic": state["content_topic"],
                "content_type": state["content_type"],
            }
        )
        state["response"].append({"extracted_persona": extracted_persona})
        return state
