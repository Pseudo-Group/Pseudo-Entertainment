"""프롬프트 템플릿을 생성하는 함수 모듈

프롬프트 템플릿을 생성하는 함수 모듈을 구성합니다.
기본적으로 PromptTemplate를 사용하여 프롬프트 템플릿을 생성하고 반환합니다.

아래는 예시입니다.
"""

from langchain_core.prompts import PromptTemplate


def get_resource_planning_prompt():
    """
    리소스 계획 수립을 위한 프롬프트 템플릿을 생성합니다.

    이 프롬프트는 다음 데이터를 입력으로 사용합니다:
    1. 프로젝트 ID: 관리할 프로젝트의 고유 ID
    2. 요청 유형: 리소스 할당, 팀 관리, 크리에이터 개발 등의 요청 유형
    3. 사용자 쿼리: 구체적인 요청사항
    4. 팀 구성원: 프로젝트에 참여하는 팀 구성원 목록
    5. 사용 가능한 리소스: 현재 사용 가능한 리소스 정보

    프롬프트는 LLM에게 주어진 정보를 기반으로 프로젝트 관리에 적합한 리소스 계획을
    수립하도록 지시합니다. 결과는 한국어로 반환됩니다.

    Returns:
        PromptTemplate: 리소스 계획 수립을 위한 프롬프트 템플릿 객체
    """
    # 리소스 계획을 위한 프롬프트 템플릿 정의
    resource_planning_template = """You are an expert entertainment project manager tasked with creating resource plans for entertainment projects. You are provided with the following information:  

1. Project ID: {project_id}  

2. Request Type: {request_type}  

3. User Query: {query}  

4. Team Members: {team_members}  

5. Available Resources: {resources_available}  

Your Task:  
Based on the information provided, develop a comprehensive resource management plan that addresses the user query. Your plan should include:  

1. PROJECT OVERVIEW:  
- Brief summary of the project based on the available information  
- Clear objectives and expected outcomes  

2. RESOURCE ALLOCATION:  
- Human resources: Team composition, roles, and responsibilities  
- Technical resources: Equipment, software, and facilities needed  
- Financial resources: Budget considerations and allocations  
- Time resources: Schedule, timeline, and milestones  

3. RESOURCE OPTIMIZATION:  
- Efficiency recommendations  
- Risk assessment and mitigation strategies  
- Contingency planning  

4. IMPLEMENTATION PLAN:  
- Step-by-step guide for executing the resource plan  
- Monitoring and evaluation mechanisms  
- Communication protocols  

5. RECOMMENDATIONS:  
- Additional resources that might be beneficial  
- Training or development opportunities  
- Process improvement suggestions  

Make your plan specific to the entertainment industry context and the particular request type. Be detailed yet concise, and ensure your recommendations are practical and actionable.  

All responses must be in Korean.  

Resource Management Plan:"""

    # PromptTemplate 객체 생성 및 반환
    return PromptTemplate(
        template=resource_planning_template,  # 정의된 프롬프트 템플릿
        input_variables=[
            "project_id",
            "request_type",
            "query",
            "team_members",
            "resources_available",
        ],  # 프롬프트에 삽입될 변수들
    )


def get_content_verification_prompt():
    """
    컨텐츠 검증 결과를 분석하는 프롬프트 템플릿을 생성합니다.

    Returns:
        PromptTemplate: 컨텐츠 검증 분석을 위한 프롬프트 템플릿 객체
    """
    content_verification_template = """당신은 엔터테인먼트 컨텐츠 관리 전문가입니다.

다음 컨텐츠 검증 결과를 분석하고 한국어로 요약해주세요:

검증 결과: {verification_result}

다음 항목들을 포함하여 분석해주세요:
1. 검증 결과 요약
2. 주요 위험 요소
3. 개선 제안사항
4. 권장 조치사항

분석 결과:"""

    return PromptTemplate(
        template=content_verification_template,
        input_variables=["verification_result"],
    )


def get_news_analysis_prompt():
    """
    뉴스 분석 결과를 요약하는 프롬프트 템플릿을 생성합니다.

    Returns:
        PromptTemplate: 뉴스 분석 요약을 위한 프롬프트 템플릿 객체
    """
    news_analysis_template = """당신은 엔터테인먼트 뉴스 분석 전문가입니다.

다음 뉴스 분석 결과를 분석하고 한국어로 요약해주세요:

뉴스 키워드: {keywords}
뉴스 결과: {news_result}

다음 항목들을 포함하여 분석해주세요:
1. 주요 뉴스 요약
2. 엔터테인먼트 산업에 미치는 영향
3. 컨텐츠 제작에 활용할 수 있는 인사이트
4. 추천 액션 아이템

분석 결과:"""

    return PromptTemplate(
        template=news_analysis_template,
        input_variables=["keywords", "news_result"],
    )


def get_trending_analysis_prompt():
    """
    트렌딩 토픽 분석 결과를 요약하는 프롬프트 템플릿을 생성합니다.

    Returns:
        PromptTemplate: 트렌딩 분석 요약을 위한 프롬프트 템플릿 객체
    """
    trending_analysis_template = """당신은 엔터테인먼트 트렌드 분석 전문가입니다.

다음 트렌딩 토픽 분석 결과를 분석하고 한국어로 요약해주세요:

트렌딩 결과: {trending_result}

다음 항목들을 포함하여 분석해주세요:
1. 주요 트렌딩 토픽 요약
2. 엔터테인먼트 산업 트렌드 분석
3. 컨텐츠 제작 기회 요소
4. 전략적 제안사항

분석 결과:"""

    return PromptTemplate(
        template=trending_analysis_template,
        input_variables=["trending_result"],
    )
