"""모델 설정 함수 모듈

기본적으로 사용할 모델 인스턴스를 설정하고 생성하고 반환시킵니다.
"""
from langchain_openai import ChatOpenAI

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
