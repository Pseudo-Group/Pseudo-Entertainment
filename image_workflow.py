import json
from typing import Dict, List, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from prompt import prompt
import base64

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda

from agents.text.modules.persona import PERSONA
from agents.image.modules.state import ImageState

from agents.image.modules.nodes import ImageGenerationNode
from agents.text.modules.nodes import PersonaExtractionNode

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp-image-generation")

template = ChatPromptTemplate.from_template(prompt)



def persona_extraction_node(state: dict) -> dict:
    persona_node = PersonaExtractionNode(name="persona_extraction")
    extracted_persona = persona_node.execute(state)
    
    return {
        "content_topic": state["content_topic"],
        "content_type": state["content_type"],
        "persona": extracted_persona
    }

def image_generation_node(state: dict) -> dict:
    image_node = ImageGenerationNode(name="image_generation")
    result = image_node.execute(state)
    return result

def build_graph():
    builder = StateGraph(dict)  # ImageState 대신 dict 사용
    builder.add_node("PersonaExtraction", RunnableLambda(persona_extraction_node))
    builder.add_node("ImageGeneration", RunnableLambda(image_generation_node))
    
    builder.set_entry_point("PersonaExtraction")
    builder.add_edge("PersonaExtraction", "ImageGeneration")
    builder.add_edge("ImageGeneration", END)  # set_finish_point 대신 END 사용

    return builder.compile()

if __name__ == "__main__":
    graph = build_graph()
    initial_state = {
        "content_topic": "마침 주말 해가 밝아와 부를 사람 하나 없지만 꺼놓은 radio 를 틀고 이 작은 city (CD) 안에 꼬인 테이프 내 맘을 달래주는 노래네 시계 소리마저 멜로딘걸 oh", 
        "content_type": "앨범 제작",
        "persona": PERSONA
    }
    result = graph.invoke(initial_state)
    print(result)



