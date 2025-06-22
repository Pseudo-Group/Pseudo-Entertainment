"""프롬프트 템플릿을 생성하는 함수 모듈

프롬프트 템플릿을 생성하는 함수 모듈을 구성합니다.
기본적으로 PromptTemplate를 사용하여 프롬프트 템플릿을 생성하고 반환합니다.
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

    Returns:
        PromptTemplate: 리소스 계획 수립을 위한 프롬프트 템플릿 객체
    """
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

All responses must be in Korean.  

Resource Management Plan:"""

    return PromptTemplate(
        template=resource_planning_template,
        input_variables=[
            "project_id",
            "request_type", 
            "query",
            "team_members",
            "resources_available",
        ],
    )


def get_search_planning_prompt():
    """
    IU 리서치를 위한 검색 계획 수립 프롬프트 템플릿을 생성합니다.
    
    Returns:
        PromptTemplate: 검색 계획 수립을 위한 프롬프트 템플릿 객체
    """
    search_planning_template = """
    당신은 웹 검색 전문가입니다.
    주어진 주제에 대한 최신 반응과 정보를 효과적으로 조사하기 위한,
    구체적이고 다양한 관점의 검색어 5개를 제안해주세요.
    각 검색어는 한 줄씩 구분해서 작성해주세요.

    주제 : {topic}
    """
    
    return PromptTemplate(
        template=search_planning_template,
        input_variables=["topic"]
    )


def get_summary_prompt():
    """
    IU 리서치 결과 요약을 위한 프롬프트 템플릿을 생성합니다.
    
    Returns:
        PromptTemplate: 요약을 위한 프롬프트 템플릿 객체
    """
    summary_template = """
    당신은 마케팅 회사의 리서치 분석가입니다.
    주어진 검색 결과들을 바탕으로, 
    '{topic}'에 대한 최신 대중 반응과 동향을 분석하여 상세한 보고서를 작성해주세요.
    
    보고서는 다음 형식을 따라 Markdown 형식으로 작성해주세요.

    # {topic} - 최신 동향 분석 보고서
    
    ## 1. 주요 동향 요약
    - (가장 중요한 핵심 동향 2~3가지를 불릿 포인트로 요약)

    ## 2. 세부 분석
    - **긍정적 반응:** (사람들이 긍정적으로 반응하는 부분과 그 이유)
    - **부정적 반응:** (사람들이 부정적으로 반응하는 부분과 그 이유)
    - **기타 주목할 만한 점:** (새로운 앨범, 작품 활동, 팬 소통, 기타 이슈 등)

    ## 3. 결론 및 종합 의견
    (전체 내용을 종합하여 현재 대중의 전반적인 반응에 대한 결론을 내리세요.)

    --- 검색 결과 원문 ---
    {search_results}
    """
    
    return PromptTemplate(
        template=summary_template,
        input_variables=["topic", "search_results"]
    )