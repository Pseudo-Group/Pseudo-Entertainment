from langchain_cohere import CohereRerank
from langchain_openai import ChatOpenAI
from langchain_upstage import UpstageEmbeddings


class Model:
    @staticmethod
    def get_embedding_model():
        return UpstageEmbeddings(model="embedding-query")

    @staticmethod
    def get_openai_single_model(temperature=0.1):
        return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)

    @staticmethod
    def get_openai_multi_model(temperature=0.1):
        return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)

    @staticmethod
    def get_rerank_model():
        return CohereRerank(model="rerank-multilingual-v3.0")
