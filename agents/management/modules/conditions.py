"""
인플루언서 이슈 분석을 위한 조건부 로직 모듈

Workflow에서 사용할 수 있는 조건부 함수들을 정의합니다.
현재는 순차적 실행 구조이므로 조건부 로직이 필요 없지만,
향후 확장을 위한 기본 구조를 제공합니다.
"""

from agents.management.modules.state import ManagementState


def should_continue_analysis(state: ManagementState) -> bool:
    """
    분석을 계속 진행해야 하는지 판단하는 함수
    
    Args:
        state: 현재 그래프 상태
        
    Returns:
        bool: 분석 계속 여부
    """
    # 에러가 발생했거나 타겟 인플루언서가 없으면 중단
    if state.get("errors") or not state.get("target_influencer"):
        return False
    
    return True


def has_sufficient_data(state: ManagementState) -> bool:
    """
    충분한 데이터가 수집되었는지 판단하는 함수
    
    Args:
        state: 현재 그래프 상태
        
    Returns:
        bool: 데이터 충분 여부
    """
    initial_results = state.get("initial_search_results", [])
    keywords = state.get("extracted_keywords", [])
    detailed_results = state.get("detailed_search_results", [])
    
    # 기본적인 데이터가 모두 있는지 확인
    return len(initial_results) > 0 and len(keywords) > 0 and len(detailed_results) > 0


def get_next_action(state: ManagementState) -> str:
    """
    현재 상태를 기반으로 다음 액션을 결정하는 함수
    
    Args:
        state: 현재 그래프 상태
        
    Returns:
        str: 다음 노드 이름
    """
    current_step = state.get("current_step", "initial")
    
    if current_step == "initial":
        return "initial_search"
    elif current_step == "initial_search_completed":
        return "keyword_extraction"
    elif current_step == "keyword_extraction_completed":
        return "detailed_search"
    elif current_step == "detailed_search_completed":
        return "issue_analysis"
    else:
        return "END"
