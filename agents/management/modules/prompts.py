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


def get_instagram_comment_analysis_prompt():
    """
    Returns a prompt template for analyzing Instagram comments in English, but output must be translated to Korean.
    """
    comment_analysis_template = """Below is a list of comments from an Instagram post. Please analyze these comments and summarize the following information in English:

1. Overall sentiment (ratio of positive/negative/neutral)
2. Main issues or discussion topics
3. Representative examples of positive, negative, and neutral comments (one each)
4. The general atmosphere and characteristics of the comments
5. Any additional noteworthy points

Comment List:
{comments}

Analysis:

Translate all your output to Korean."""

    return PromptTemplate(
        template=comment_analysis_template,
        input_variables=["comments"],
    )
