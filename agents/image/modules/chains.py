"""LangChain 체인을 설정하는 함수 모듈

LCEL(LangChain Expression Language)을 사용하여 체인을 구성합니다.
기본적으로 modules.prompt 템플릿과 modules.models 모듈을 사용하여 LangChain 체인을 생성합니다.
"""

# from langchain.schema.runnable import RunnablePassthrough, RunnableSerializable
# from langchain_core.output_parsers import StrOutputParser

# from agents.image.modules.models import get_openai_model
# from agents.image.modules.prompts import get_image_generation_prompt

# chains.py
import os

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from pydantic import SecretStr

from agents.image.modules.prompts import outfit_prompt_template

load_dotenv()  # .env 파일에서 환경변수 로딩


def get_outfit_prompt_chain():
    llm = ChatGroq(
        api_key=SecretStr(os.getenv("GROQ_API_KEY") or ""),
        model="llama3-8b-8192",
        temperature=0,
    )
    return LLMChain(llm=llm, prompt=outfit_prompt_template)


def get_llm():
    return ChatGroq(
        api_key=SecretStr(os.getenv("GROQ_API_KEY") or ""),
        model="llama3-8b-8192",
        temperature=0,
    )


# def set_image_generation_chain() -> RunnableSerializable:
#     """
#     이미지 생성에 사용할 LangChain 체인을 생성합니다.
#
#     체인은 다음 단계로 구성됩니다:
#     1. 입력에서 query를 추출하여 프롬프트에 전달
#     2. 프롬프트 템플릿에 값을 삽입하여 최종 프롬프트 생성
#     3. LLM을 호출하여 이미지 생성 수행
#     4. 결과를 문자열로 변환
#
#     이 함수는 이미지 생성 노드에서 사용됩니다.
#
#     Returns:
#         RunnableSerializable: 실행 가능한 체인 객체
#     """
#     # 이미지 생성을 위한 프롬프트 가져오기
#     prompt = get_image_generation_prompt()
#     # OpenAI 모델 가져오기
#     model = get_openai_model()
#
#     # LCEL을 사용하여 체인 구성
#     return (
#         # 입력에서 필요한 필드 추출 및 프롬프트에 전달
#         RunnablePassthrough.assign(
#             query=lambda x: x["query"],  # 사용자 쿼리 추출
#         )
#         | prompt  # 프롬프트 적용
#         | model   # LLM 모델 호출
#         | StrOutputParser()  # 결과를 문자열로 변환
#     )
