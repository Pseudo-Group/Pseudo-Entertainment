"""모델 설정 함수 모듈

기본적으로 사용할 모델 인스턴스를 설정하고 생성하고 반환시킵니다.
"""
from langchain_openai import ChatOpenAI

from google import genai
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os 

load_dotenv()

YOUTUBE_API_SERVICE_NAME = os.getenv("YOUTUBE_API_SERVICE_NAME")
YOUTUBE_API_VERSION = os.getenv("YOUTUBE_API_VERSION")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_openai_model(temperature=0.7, top_p=0.9):
    """
    LangChain에서 사용할 OpenAI 모델을 초기화하여 반환합니다.

    환경변수에서 OPENAI_API_KEY를 가져와 사용하기 때문에, .env 파일에 유효한 API 키가 설정되어 있어야 합니다.

    Returns:
        ChatOpenAI: 초기화된 OpenAI 모델 인스턴스
    """
    # OpenAI 모델 초기화 및 반환
    return ChatOpenAI(model="gpt-4o-mini", 
                      temperature=temperature, 
                      top_p=top_p,
                      )

def get_youtube_client():
    """
    Youtube 영상 검색 API에 사용하기 위한 client, 즉 서비스 객체를 제작합니다.

    환경변수에서 YOUTUBE_API_KEY, YOUTUBE_API_SERVICE_NAME, 
    YOUTUBE_API_VERSION을 가져와 사용하기 때문에, .env 파일에 유효한 
    API 키가 설정되어 있어야 합니다.

    Returns:
        build: 초기화된 youtube client 인스턴스
    """
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                        developerKey = YOUTUBE_API_KEY)

def get_gemini_client():
    """
    LangChain에서 사용할 Gemini client을 초기화하여 반환합니다.

    환경변수에서 GEMINI_API_KEY를 가져와 사용하기 때문에, 
    .env 파일에 유효한 API 키가 설정되어 있어야 합니다.

    노드에서 Gemini 모델을 사용할 때 모델명을 따로 정의해줘야 합니다.

    Returns:
        genai.Client: 초기화된 Gemini client 인스턴스
    """
    #Gemini 모델 초기화 및 반환
    return genai.Client(api_key = GEMINI_API_KEY)

