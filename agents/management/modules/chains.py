"""LangChain 체인을 설정하는 함수 모듈

LCEL(LangChain Expression Language)을 사용하여 체인을 구성합니다.
기본적으로 modules.prompt 템플릿과 modules.models 모듈을 사용하여 LangChain 체인을 생성합니다.
"""

from langchain.schema.runnable import RunnablePassthrough, RunnableSerializable
from langchain_core.output_parsers import StrOutputParser

from agents.management.modules.models import get_openai_model
from agents.management.modules.prompts import (
    get_resource_planning_prompt,
    get_search_planning_prompt,
    get_summary_prompt
)


def set_resource_planning_chain() -> RunnableSerializable:
    """
    리소스 계획 수립에 사용할 LangChain 체인을 생성합니다.

    이 함수는 LCEL(LangChain Expression Language)을 사용하여 체인을 구성합니다.
    체인은 다음 단계로 구성됩니다:
    1. 입력에서 project_id, request_type, query, team_members 등을 추출하여 프롬프트에 전달
    2. 프롬프트 템플릿에 값을 삽입하여 최종 프롬프트 생성
    3. LLM을 호출하여 리소스 계획 생성 수행
    4. 결과를 문자열로 변환

    Returns:
        RunnableSerializable: 실행 가능한 체인 객체
    """
    prompt = get_resource_planning_prompt()
    model = get_openai_model()

    return (
        RunnablePassthrough.assign(
            project_id=lambda x: x["project_id"],
            request_type=lambda x: x["request_type"],
            query=lambda x: x["query"],
            team_members=lambda x: x.get("team_members", []),
            resources_available=lambda x: x.get("resources_available", {}),
        )
        | prompt
        | model
        | StrOutputParser()
    )


def set_search_planning_chain() -> RunnableSerializable:
    """
    IU 리서치를 위한 검색 계획 수립에 사용할 LangChain 체인을 생성합니다.

    이 함수는 LCEL을 사용하여 체인을 구성합니다.
    체인은 다음 단계로 구성됩니다:
    1. 입력에서 topic을 추출하여 프롬프트에 전달
    2. 프롬프트 템플릿에 값을 삽입하여 최종 프롬프트 생성
    3. LLM을 호출하여 검색어 생성
    4. 결과를 문자열로 변환

    Returns:
        RunnableSerializable: 실행 가능한 체인 객체
    """
    prompt = get_search_planning_prompt()
    model = get_openai_model()

    return (
        RunnablePassthrough.assign(
            topic=lambda x: x["topic"]
        )
        | prompt
        | model
        | StrOutputParser()
    )


def set_summary_chain() -> RunnableSerializable:
    """
    IU 리서치 결과 요약에 사용할 LangChain 체인을 생성합니다.

    이 함수는 LCEL을 사용하여 체인을 구성합니다.
    체인은 다음 단계로 구성됩니다:
    1. 입력에서 topic과 search_results를 추출하여 프롬프트에 전달
    2. 프롬프트 템플릿에 값을 삽입하여 최종 프롬프트 생성
    3. LLM을 호출하여 요약 보고서 생성
    4. 결과를 문자열로 변환

    Returns:
        RunnableSerializable: 실행 가능한 체인 객체
    """
    prompt = get_summary_prompt()
    model = get_openai_model()

    return (
        RunnablePassthrough.assign(
            topic=lambda x: x["topic"],
            search_results=lambda x: x["search_results"]
        )
        | prompt
        | model
        | StrOutputParser()
    )