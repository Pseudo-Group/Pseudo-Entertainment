from langchain.schema.runnable import RunnablePassthrough, RunnableSerializable
from langchain_core.output_parsers import StrOutputParser

from agents.text.modules.models import get_openai_model
from agents.text.modules.prompts import get_extraction_prompt


def set_extraction_chain() -> RunnableSerializable:
    """페르소나 추출에 사용할 체인

    Returns:
        RunnableSerializable: 페르소나 추출 체인
    """
    prompt = get_extraction_prompt()
    model = get_openai_model()

    return (
        RunnablePassthrough.assign(
            content_topic=lambda x: x["content_topic"],
            content_type=lambda x: x["content_type"],
        )
        | prompt
        | model
        | StrOutputParser()
    )
