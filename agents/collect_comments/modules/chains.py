"""LangChain 체인을 설정하는 함수 모듈

LCEL(LangChain Expression Language)을 사용하여 체인을 구성합니다.
기본적으로 modules.prompt 템플릿과 modules.models 모듈을 사용하여 LangChain 체인을 생성합니다.

"""

from langchain.schema.runnable import RunnablePassthrough, RunnableSerializable
from langchain_core.output_parsers import StrOutputParser

from agents.management.modules.models import get_openai_model
from agents.management.modules.prompts import get_resource_planning_prompt


def set_resource_planning_chain() -> RunnableSerializable:
    """
    리소스 계획 수립에 사용할 LangChain 체인을 생성합니다.

    이 함수는 LCEL(LangChain Expression Language)을 사용하여 체인을 구성합니다.
    체인은 다음 단계로 구성됩니다:
    1. 입력에서 project_id, request_type, query, team_members 등을 추출하여 프롬프트에 전달
    2. 프롬프트 템플릿에 값을 삽입하여 최종 프롬프트 생성
    3. LLM을 호출하여 리소스 계획 생성 수행
    4. 결과를 문자열로 변환

    이 함수는 리소스 관리 노드에서 사용됩니다.

    Returns:
        RunnableSerializable: 실행 가능한 체인 객체
    """
    # 리소스 계획을 위한 프롬프트 가져오기
    prompt = get_resource_planning_prompt()
    # OpenAI 모델 가져오기
    model = get_openai_model()

    # LCEL을 사용하여 체인 구성
    return (
        # 입력에서 필요한 필드 추출 및 프롬프트에 전달
        RunnablePassthrough.assign(
            project_id=lambda x: x["project_id"],  # 프로젝트 ID 추출
            request_type=lambda x: x["request_type"],  # 요청 유형 추출
            query=lambda x: x["query"],  # 사용자 쿼리 추출
            team_members=lambda x: x.get("team_members", []),  # 팀 구성원 추출
            resources_available=lambda x: x.get(
                "resources_available", {}
            ),  # 가용 리소스 추출
        )
        | prompt  # 프롬프트 적용
        | model  # LLM 모델 호출
        | StrOutputParser()  # 결과를 문자열로 변환
    )
