"""모델 설정 함수 모듈

기본적으로 사용할 모델 인스턴스를 설정하고 생성하고 반환시킵니다.
"""

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI


def get_openai_model(temperature=0.7, top_p=0.9):
    """
    LangChain에서 사용할 OpenAI 모델을 초기화하여 반환합니다.

    환경변수에서 OPENAI_API_KEY를 가져와 사용하기 때문에, .env 파일에 유효한 API 키가 설정되어 있어야 합니다.

    Returns:
        ChatOpenAI: 초기화된 OpenAI 모델 인스턴스
    """
    # OpenAI 모델 초기화 및 반환
    return ChatOpenAI(model="gpt-4o-mini", temperature=temperature, top_p=top_p)


def get_groq_model(model_name="llama3-8b-8192", temperature=0.7, top_p=0.9):
    """
    Groq API를 사용하는 Llama3 기반 모델을 LangChain에서 가져옵니다.
    사용 가능한 모델 예: "llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"
    """
    return ChatGroq(
        model_name=model_name,
        temperature=temperature,
        top_p=top_p,
    )
