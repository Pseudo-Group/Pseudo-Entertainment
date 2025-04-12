from langchain_openai import ChatOpenAI

@dataclass(kw_only=True)
class Model:
    def get_openai_model(temperature=0.7, top_p=0.9):
        return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
    
    def get_openai_multi_model(temperature=0.7):
        return ChatOpenAI(model="gpt-4o", temperature=temperature)
