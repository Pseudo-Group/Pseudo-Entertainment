"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.
"""

import os
import base64
from datetime import datetime
from agents.base_node import BaseNode
from agents.image.modules.chains import set_image_generation_chain
from typing import Dict, Any
from langchain_core.runnables import RunnableSerializable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

from agents.text.modules.persona import PERSONA
from agents.base_node import BaseNode
from agents.image.modules.state import ImageState
from agents.image.modules.prompts import get_image_generation_prompt


load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class ImageGenerationNode(BaseNode):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp-image-generation")
        self.chain = set_image_generation_chain()
        self.prompt = get_image_generation_prompt()
   

    def execute(self, state: ImageState) -> dict:
        prompt_chain = self.chain
        
        response = prompt_chain.invoke(
            {
                "content_topic": state["content_topic"],  # 콘텐츠 주제
                "content_type": state["content_type"],  # 콘텐츠 유형
                "persona_details": PERSONA,  # 페르소나 세부 정보
            }
        , generation_config = dict(response_modalities = ["TEXT", "IMAGE"]))
        
        image_base64 = response.content[1].get("image_url").get("url").split(",")[-1]
        image_data = base64.b64decode(image_base64)
        
        with open("output.png", "wb") as f: 
            f.write(image_data)
        
        return state



