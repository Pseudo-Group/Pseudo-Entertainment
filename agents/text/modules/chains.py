"""LangChain 체인를 설정하는 함수 모듈

LCEL(LangChain Expression Language)을 사용하여 체인을 구성합니다.
기본적으로 modules.prompt 템플릿과 modules.models 모듈을 사용하여 LangChain 체인를 생성합니다.

"""

from langchain.schema.runnable import RunnablePassthrough, RunnableSerializable
from langchain_core.output_parsers import StrOutputParser

from agents.text.modules.models import get_openai_model
from agents.text.modules.prompts import get_extraction_prompt


def set_extraction_chain() -> RunnableSerializable:
    """
    페르소나 추출에 사용할 LangChain 체인을 생성합니다.

    이 함수는 LCEL(LangChain Expression Language)을 사용하여 체인을 구성합니다.
    체인은 다음 단계로 구성됩니다:
    1. 입력에서 content_topic과 content_type을 추출하여 프롬프트에 전달
    2. 프롬프트 템플릿에 값을 삽입하여 최종 프롬프트 생성
    3. LLM을 호출하여 페르소나 추출 수행
    4. 결과를 문자열로 변환

    이 함수는 페르소나 추출 노드에서 사용됩니다.
    ```

    Returns:
        RunnableSerializable: 실행 가능한 체인 객체
    """
    # 페르소나 추출을 위한 프롬프트 가져오기
    prompt = get_extraction_prompt()
    # OpenAI 모델 가져오기
    model = get_openai_model()

    # LCEL을 사용하여 체인 구성
    return (
        # 입력에서 필요한 필드 추출 및 프롬프트에 전달
        RunnablePassthrough.assign(
            content_topic=lambda x: x["content_topic"],  # 콘텐츠 주제 추출
            content_type=lambda x: x["content_type"],  # 콘텐츠 유형 추출
        )
        | prompt  # 프롬프트 적용
        | model  # LLM 모델 호출
        | StrOutputParser()  # 결과를 문자열로 변환
    )
