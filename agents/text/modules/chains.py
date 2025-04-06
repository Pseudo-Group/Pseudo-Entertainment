from langchain.schema.runnable import RunnablePassthrough, RunnableSerializable
from langchain_core.output_parsers import StrOutputParser

from agents.models import Model
from agents.text.modules.prompts import PersonaPrompt


class PersonaChain:
    @staticmethod
    def set_extraction_chain() -> RunnableSerializable:
        """PersonaExtractionNode에서 사용할 체인"""
        prompt = PersonaPrompt.get_extraction_prompt()
        model = Model.get_openai_multi_model()
        return (
            RunnablePassthrough.assign(
                content_topic=lambda x: x["content_topic"],
                content_type=lambda x: x["content_type"],
            )
            | prompt
            | model
            | StrOutputParser()
        )
    