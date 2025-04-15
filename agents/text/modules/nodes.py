from agents.base_node import BaseNode
from agents.text.modules.chains import set_extraction_chain


class PersonaExtractionNode(BaseNode):
    """콘텐츠 종류에 적합한 페르소나를 추출하는 노드"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chain = set_extraction_chain()

    def execute(self, state) -> dict:
        extracted_persona = self.chain.invoke(
            {
                "content_topic": state["content_topic"],
                "content_type": state["content_type"],
            }
        )

        return {"response": extracted_persona}
