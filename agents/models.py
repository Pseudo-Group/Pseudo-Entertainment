from langchain_openai import ChatOpenAI


class Model:
    @staticmethod
    def get_openai_single_model(temperature=0.1):
        return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)

    @staticmethod
    def get_openai_multi_model(temperature=0.1):
        return ChatOpenAI(model="gpt-4o", temperature=temperature)
