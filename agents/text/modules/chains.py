"""LangChain 체인를 설정하는 함수 모듈

LCEL(LangChain Expression Language)을 사용하여 체인을 구성합니다.
기본적으로 modules.prompt 템플릿과 modules.models 모듈을 사용하여 LangChain 체인를 생성합니다.

"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough,
    RunnableSerializable,
)

from agents.text.mcp.mcp_client import scrape_news
from agents.text.modules.models import get_openai_model
from agents.text.modules.persona import PERSONA
from agents.text.modules.prompts import (
    get_extraction_prompt,
    get_instagram_text_prompt,
    get_news_scraping_query_prompt,
    get_topic_from_news_prompt,
)


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
            persona_details=lambda x: PERSONA,
        )
        | prompt  # 프롬프트 적용
        | model  # LLM 모델 호출
        | StrOutputParser()  # 결과를 문자열로 변환
    )


def set_topic_generation_news_chain() -> RunnableSerializable:
    """
    뉴스로부터 텍스트 콘텐츠 주제를 추출하는 LangChain 체인을 생성합니다.
    """
    news_scraping_query_prompt = get_news_scraping_query_prompt()
    model = get_openai_model()

    # 문자열 입력을 딕셔너리로 변환
    input_transformer = RunnableLambda(lambda x: {"query": x})

    news_scraping_query_chain = (
        input_transformer
        | RunnablePassthrough.assign(persona_details=lambda x: PERSONA)
        | news_scraping_query_prompt
        | model
        | StrOutputParser()  # 결과를 문자열로 변환
    )

    return (
        news_scraping_query_chain
        | RunnableLambda(scrape_news)  # 비동기 함수를 그대로 사용
        | RunnablePassthrough.assign(
            news_article=lambda x: x,
            persona_details=lambda x: PERSONA,
        )
        | get_topic_from_news_prompt()
        | model
        | StrOutputParser()
    )


def set_instagram_text_chain() -> RunnableSerializable:
    """
    인스타그램 텍스트 생성에 사용할 LangChain 체인을 생성합니다.

    이 함수는 LCEL(LangChain Expression Language)을 사용하여 체인을 구성합니다.
    체인은 다음 단계로 구성됩니다:
    1. 입력에서 persona_extracted를 추출하여 프롬프트에 전달
    2. 프롬프트 템플릿에 값을 삽입하여 최종 프롬프트 생성
    3. LLM을 호출하여 인스타그램 텍스트 생성 수행
    4. 결과를 문자열로 변환

    이 함수는 GenTextNode에서 사용됩니다.

    Returns:
        RunnableSerializable: 실행 가능한 체인 객체
    """
    # 인스타그램 텍스트 생성을 위한 프롬프트 가져오기
    prompt = get_instagram_text_prompt()
    # OpenAI 모델 가져오기
    model = get_openai_model()

    # LCEL을 사용하여 체인 구성
    return (
        # 입력에서 필요한 필드 추출 및 프롬프트에 전달
        RunnablePassthrough.assign(
            persona_extracted=lambda x: x["persona_extracted"],  # 추출된 페르소나
        )
        | prompt  # 프롬프트 적용
        | model  # LLM 모델 호출
        | StrOutputParser()  # 결과를 문자열로 변환
    )
