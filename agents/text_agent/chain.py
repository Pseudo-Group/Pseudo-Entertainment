from operator import itemgetter

from langchain.schema.runnable import RunnablePassthrough
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser

from agents.manager_agent.prompt import Prompt
from agents.model import Model


class TextChain:
    @staticmethod
    def set_hyde_chain(mode: str):
        """HyDE 노드에서 사용할 체인"""
        if mode == "single":
            prompt = Prompt.get_hyde_single_prompt()
            model = Model.get_openai_single_model()

            return (
                RunnablePassthrough.assign(query=lambda x: x["query"])
                | prompt
                | model
                | StrOutputParser()
            )

        elif mode == "multi":
            model = Model.get_openai_multi_model()
            prompt = Prompt.get_hyde_multi_prompt()

            def create_messages(input_dict):
                return [
                    HumanMessage(
                        content=[
                            {"type": "text", "text": input_dict["prompt_text"]},
                            {
                                "type": "image_url",
                                "image_url": {"url": input_dict["image"]},
                            },
                        ]
                    )
                ]

            return (
                RunnablePassthrough.assign(
                    prompt_text=lambda x: prompt.format(query=x["query"]),
                    image=itemgetter("image"),
                )
                | create_messages
                | model
                | StrOutputParser()
            )
