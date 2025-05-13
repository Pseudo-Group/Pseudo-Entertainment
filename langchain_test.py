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

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp-image-generation")

template = ChatPromptTemplate.from_template(prompt)

def input_node(state: dict) -> dict:
    required_keys = ["purpose","text"]

    for key in required_keys:
        if key not in state:
            raise ValueError("Missing required input: '{key}'")
    
    # 목적과 텍스트 출력 (디버깅용)
    # print(f"[InputNode] 목적: {state['purpose']}")
    # print(f"[InputNode] 텍스트: {state['text']}")

    return {
        "purpose":state["purpose"],
        "text":state["text"]
    }

def gemini_image_generation_node(state:dict) -> dict:
    purpose = state["purpose"]
    text = state["text"]

    prompt_chain = template | llm 

    response = prompt_chain.invoke({"purpose":purpose, "text":text}, generation_config = dict(response_modalities = ["TEXT", "IMAGE"]))
    
    image_base64 = response.content[0].get("image_url").get("url").split(",")[-1]
    image_data = base64.b64decode(image_base64)
    
    with open("output.png", "wb") as f: 
        f.write(image_data)
    
def build_graph():
    builder = StateGraph(dict)
    builder.add_node("Input", RunnableLambda(input_node))
    builder.add_node("geminiNode", RunnableLambda(gemini_image_generation_node))
    
    builder.set_entry_point("Input")
    builder.add_edge("Input", "geminiNode")
    builder.add_edge("geminiNode", END)

    return builder.compile()

if __name__ == "__main__":
    graph = build_graph()
    result = graph.invoke({
        "purpose": "앨범 제작",
        "text": "마침 주말 해가 밝아와 부를 사람 하나 없지만 꺼놓은 radio 를 틀고 이 작은 city (CD) 안에 꼬인 테이프 내 맘을 달래주는 노래네 시계 소리마저 멜로딘걸 oh"
    })



