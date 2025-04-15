from langchain_openai import ChatOpenAI


def get_openai_model(temperature=0.7, top_p=0.9):
    return ChatOpenAI(model="gpt-4o-mini", temperature=temperature, top_p=top_p)
