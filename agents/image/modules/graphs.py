from langgraph.graph import StateGraph, END
from langgraph.graph.graph import Runnable 
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser

# from agents.image.modules.models import get_openai_model
from agents.image.modules.models import get_gemini_model
from agents.image.modules.prompts import get_image_generation_prompt, get_text_response_prompt
from agents.image.modules.state import ImageState

import base64

#1. 준비
prompt = get_image_generation_prompt()
model = get_gemini_model()

def extract_fields(state:ImageState)->ImageState:
    text = state.get("text", "")
    purpose = state.get("purpose", "")
    return {
        "text": text,
        "purpose": purpose,
        } 

def gemini_image_generation_node(state:dict):
    
    template = get_image_generation_prompt()
    purpose = state["purpose"]
    text = state["text"]
    message = template.format(purpose = purpose, text = text)

    model = get_gemini_model()

    response = model.invoke(message, generation_config = dict(response_modalities = ["TEXT" ,"IMAGE"]))
    
    image_base64 = response.content[1].get("image_url").get("url").split(",")[-1]
    image_data = base64.b64decode(image_base64)
    
    with open("output.png", "wb") as f: 
        f.write(image_data)
    
    return image_base64
    

def gemini_text_response_node(state:dict):
    template = get_text_response_prompt()
    purpose = state["purpose"]
    text = state["text"]
    message = template.format(purpose=purpose, text=text)

    model = get_gemini_model()
    response = model.invoke(message)
    
    return response.content

def set_image_generation_graph() -> Runnable:

    builder = StateGraph(dict)
    builder.add_node("Input", RunnableLambda(extract_fields))
    builder.add_node("geminiNode", RunnableLambda(gemini_image_generation_node))
    
    builder.set_entry_point("Input")
    builder.add_edge("Input", "geminiNode")
    builder.add_edge("geminiNode", END)


    return builder.compile()

def set_text_response_graph() -> Runnable:
    builder = StateGraph(dict)
    builder.add_node("Input", RunnableLambda(extract_fields))
    builder.add_node("geminiNode", RunnableLambda(gemini_text_response_node))
    
    builder.set_entry_point("Input")
    builder.add_edge("Input", "geminiNode")
    builder.add_edge("geminiNode", END)

    return builder.compile()