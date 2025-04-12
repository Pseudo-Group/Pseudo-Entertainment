from operator import itemgetter

from langchain.schema.runnable import RunnablePassthrough
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser

from agents.manager.modules.prompts import Prompt
from agents.models import Model


class Chain:
    """
    LCEL 체인 저장소
    """

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

    @staticmethod
    def set_rewrite_chain():
        """Re-write 노드에서 사용할 체인"""
        prompt = Prompt.get_rewrite_prompt()
        model = Model.get_openai_single_model()

        return (
            RunnablePassthrough.assign(
                query=lambda x: x["query"],
                hypothetical_doc=lambda x: x["hypothetical_doc"],
            )
            | prompt
            | model
            | StrOutputParser()
        )

    @staticmethod
    def set_judge_chain():
        """Judge 노드에서 사용할 체인"""
        prompt = Prompt.get_judge_prompt()
        model = Model.get_openai_multi_model(temperature=0.45)

        return (
            RunnablePassthrough.assign(
                query=lambda x: x["query"],
                chat_history=lambda x: x["chat_history"],
                documents=lambda x: x["documents"],
            )
            | prompt
            | model
            | StrOutputParser()
        )

    @staticmethod
    def set_history_title_chain():
        """Judge 노드에서 사용할 체인"""
        prompt = Prompt.get_history_title_prompt()
        model = Model.get_openai_single_model(temperature=0.6)

        return (
            RunnablePassthrough.assign(
                element=lambda x: x["element"],
            )
            | prompt
            | model
            | StrOutputParser()
        )

    @staticmethod
    def set_high_similarity_generator_chain():
        """High Similarity Generator 노드에서 사용할 체인"""
        prompt = Prompt.get_high_similarity_generator_prompt()
        model = Model.get_openai_single_model(temperature=0.2)

        return (
            RunnablePassthrough.assign(
                query=lambda x: x["query"],
                ranked_exhibitions=lambda x: x["ranked_exhibitions"],
                scoring_info=lambda x: x["scoring_info"],
            )
            | prompt
            | model
            | StrOutputParser()
        )

    @staticmethod
    def set_low_similarity_generator_chain():
        """Low Similarity Generator 노드에서 사용할 체인"""
        prompt = Prompt.get_low_similarity_generator_prompt()
        model = Model.get_openai_single_model(temperature=0.2)

        return (
            RunnablePassthrough.assign(
                query=lambda x: x["query"],
                ranked_exhibitions=lambda x: x["ranked_exhibitions"],
            )
            | prompt
            | model
            | StrOutputParser()
        )
