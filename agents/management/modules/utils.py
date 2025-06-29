"""
02_data_model.md에 정의된 데이터 검증, 변환, 유틸리티 함수 모듈

섹션 3: 데이터 검증 규칙
섹션 4: 데이터 변환 규칙  
섹션 6: 유틸리티 함수
"""

import json
import re
from typing import List, Dict, Any
from datetime import datetime
from urllib.parse import urlparse

from agents.management.modules.models import SearchResult, IssueAnalysis
from agents.management.modules.state import ManagementState


class LLMResponseError(Exception):
    """LLM 응답 변환 실패 예외"""
    pass


# ============================================================================
# 섹션 3: 데이터 검증 규칙
# ============================================================================

def validate_query(query: str) -> bool:
    """
    검색 쿼리 유효성 검증
    02_data_model.md 섹션 3.1
    """
    return (
        isinstance(query, str) and
        len(query.strip()) > 0 and
        len(query) <= 100
    )


def validate_search_result(result: SearchResult) -> bool:
    """
    검색 결과 유효성 검증
    02_data_model.md 섹션 3.2
    """
    return (
        len(result.title) > 0 and
        len(result.content) > 0 and
        result.url.startswith(('http://', 'https://')) and
        0.0 <= result.relevance_score <= 1.0 and
        len(result.published_date) > 0
    )


def validate_issue_analysis(analysis: IssueAnalysis) -> bool:
    """
    이슈 분석 결과 유효성 검증
    02_data_model.md 섹션 3.3
    """
    valid_categories = ['발언', '행동', '컨텐츠', '개인']
    return (
        isinstance(analysis.is_issue, bool) and
        1 <= analysis.severity_level <= 4 and
        analysis.issue_category in valid_categories and
        0.0 <= analysis.confidence_score <= 1.0 and
        len(analysis.summary) > 0
    )


# ============================================================================
# 섹션 4: 데이터 변환 규칙
# ============================================================================

def convert_tavily_to_search_result(tavily_result: Dict) -> SearchResult:
    """
    Tavily 응답을 SearchResult로 변환
    02_data_model.md 섹션 4.1
    """
    return SearchResult(
        title=_extract_title_from_url(tavily_result.get("url", "")),
        content=_truncate_content(tavily_result.get("content", "")),
        url=tavily_result.get("url", ""),
        published_date=_estimate_date(),  # 최근 날짜로 추정
        source=_extract_source_from_url(tavily_result.get("url", "")),
        relevance_score=float(tavily_result.get("score", 0.0)),
        snippet=_generate_snippet(tavily_result.get("content", ""))
    )


def convert_llm_to_issue_analysis(
    llm_response: str,
    original_result: SearchResult
) -> IssueAnalysis:
    """
    LLM JSON 응답을 IssueAnalysis로 변환
    02_data_model.md 섹션 4.2
    """
    try:
        data = json.loads(llm_response)
        return IssueAnalysis(
            original_result=original_result,
            is_issue=bool(data.get("is_issue", False)),
            severity_level=int(data.get("severity_level", 1)),
            issue_category=str(data.get("issue_category", "기타")),
            summary=_truncate_text(data.get("summary", ""), 200),
            potential_impact=_truncate_text(data.get("potential_impact", ""), 300),
            confidence_score=float(data.get("confidence_score", 0.0)),
            analysis_reasoning=_truncate_text(data.get("reasoning", ""), 400)
        )
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise LLMResponseError(f"LLM 응답 변환 실패: {e}")


# ============================================================================
# 섹션 5: 상태 업데이트 및 접근 패턴
# ============================================================================

def update_state(current_state: ManagementState, updates: Dict) -> Dict:
    """
    상태 업데이트 헬퍼 함수
    02_data_model.md 섹션 5.1
    """
    return {
        **updates,  # 새로운 데이터
        "response": ["처리 완료 메시지"]
    }


def get_search_results(state: ManagementState) -> List[SearchResult]:
    """
    검색 결과 안전 접근
    02_data_model.md 섹션 5.2
    """
    return state.get("initial_search_results", [])


def get_keywords(state: ManagementState) -> List[str]:
    """
    키워드 안전 접근
    02_data_model.md 섹션 5.2
    """
    return state.get("extracted_keywords", [])


def get_detailed_results(state: ManagementState) -> List[SearchResult]:
    """세부 검색 결과 안전 접근"""
    return state.get("detailed_search_results", [])


def get_analyzed_issues(state: ManagementState) -> List[IssueAnalysis]:
    """분석된 이슈 안전 접근"""
    return state.get("analyzed_issues", [])


# ============================================================================
# 섹션 6: 유틸리티 함수
# ============================================================================

def clean_text_simple(text: str, max_length: int = 8000) -> str:
    """
    간단한 텍스트 정리 (05_workflow_and_process.md 섹션 4.2.1)
    
    Args:
        text: 정리할 텍스트
        max_length: 최대 길이 제한
        
    Returns:
        str: 정리된 텍스트
    """
    import re
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 연속된 공백 정리
    text = re.sub(r'\s+', ' ', text)
    
    # 길이 제한
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    
    return text.strip()


def clean_keywords_simple(keywords: List[str]) -> List[str]:
    """
    간단한 키워드 정리 (05_workflow_and_process.md 섹션 4.2.2)
    
    Args:
        keywords: 정리할 키워드 리스트
        
    Returns:
        List[str]: 정리된 키워드 리스트
    """
    cleaned = []
    for keyword in keywords:
        # 공백 제거 및 길이 확인
        clean_keyword = keyword.strip()
        if 2 <= len(clean_keyword) <= 20:
            cleaned.append(clean_keyword)
    
    # 중복 제거 (순서 유지)
    return list(dict.fromkeys(cleaned))


def get_required_data(state: ManagementState, node_type: str) -> Dict:
    """
    노드별 필수 데이터 추출 (05_workflow_and_process.md 섹션 4.1.1)
    
    Args:
        state: 현재 상태
        node_type: 노드 타입
        
    Returns:
        Dict: 노드별 필수 데이터
    """
    if node_type == "initial_search":
        return {"query": state["query"]}
    
    elif node_type == "keyword_extraction":
        return {"initial_search_results": state.get("initial_search_results", [])}
    
    elif node_type == "detailed_search":
        return {"extracted_keywords": state.get("extracted_keywords", [])}
    
    elif node_type == "issue_analysis":
        return {"detailed_search_results": state.get("detailed_search_results", [])}
    
    return {}


def validate_intermediate_results(state: ManagementState, stage: str) -> bool:
    """
    중간 결과 유효성 검증 (05_workflow_and_process.md 섹션 4.1.2)
    
    Args:
        state: 현재 상태
        stage: 검증할 단계
        
    Returns:
        bool: 유효성 여부
    """
    validations = {
        "after_initial_search": lambda s: bool(s.get("initial_search_results")),
        "after_keyword_extraction": lambda s: bool(s.get("extracted_keywords")),
        "after_detailed_search": lambda s: bool(s.get("detailed_search_results")),
        "after_issue_analysis": lambda s: "analyzed_issues" in s
    }
    
    return validations.get(stage, lambda s: True)(state)


async def api_call_with_basic_retry(api_function, max_retries: int = 2):
    """
    기본 재시도 로직 (05_workflow_and_process.md 섹션 3.2.1)
    
    Args:
        api_function: 실행할 API 함수
        max_retries: 최대 재시도 횟수
        
    Returns:
        API 함수 실행 결과
    """
    import asyncio
    
    for attempt in range(max_retries):
        try:
            return await api_function()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            await asyncio.sleep(1)  # 1초 대기


def _truncate_content(content: str, max_length: int = 500) -> str:
    """
    내용을 지정된 길이로 자르기
    02_data_model.md 섹션 6.1
    """
    if len(content) <= max_length:
        return content
    return content[:max_length-3] + "..."


def _extract_source_from_url(url: str) -> str:
    """
    URL에서 출처 추출
    02_data_model.md 섹션 6.1
    """
    parsed = urlparse(url)
    domain = parsed.netloc
    # 간단한 도메인명 추출 로직
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain.split('.')[0] if domain else "알 수 없음"


def _generate_snippet(content: str, max_length: int = 100) -> str:
    """
    스니펫 생성
    02_data_model.md 섹션 6.1
    """
    return _truncate_content(content, max_length)


def _estimate_date() -> str:
    """
    현재 날짜를 ISO 8601 형식으로 반환
    02_data_model.md 섹션 6.2
    """
    return datetime.utcnow().isoformat() + "Z"


def _extract_title_from_url(url: str) -> str:
    """
    URL에서 제목 추정 (간단한 휴리스틱)
    02_data_model.md 섹션 6.2
    """
    parsed = urlparse(url)
    path = parsed.path
    if path:
        # 경로의 마지막 부분을 제목으로 사용
        title = path.split('/')[-1].replace('-', ' ').replace('_', ' ')
        return title if title else "제목 없음"
    return "제목 없음"


def _truncate_text(text: str, max_length: int) -> str:
    """텍스트를 지정된 길이로 자르기"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


# ============================================================================
# 추가 유틸리티 함수들
# ============================================================================

def format_search_results_for_display(results: List[SearchResult]) -> str:
    """검색 결과를 읽기 쉬운 텍스트 형태로 포맷팅"""
    if not results:
        return "검색 결과가 없습니다."
    
    formatted_text = ""
    for i, result in enumerate(results, 1):
        formatted_text += f"[결과 {i}]\n"
        formatted_text += f"제목: {result.title}\n"
        formatted_text += f"내용: {result.snippet}\n"
        formatted_text += f"출처: {result.source}\n"
        formatted_text += f"관련성: {result.relevance_score:.2f}\n"
        formatted_text += f"URL: {result.url}\n\n"
    
    return formatted_text


def create_analysis_summary(state: ManagementState) -> Dict[str, Any]:
    """분석 결과의 요약 정보를 생성"""
    analyzed_issues = get_analyzed_issues(state)
    
    # 이슈 통계
    total_issues = len(analyzed_issues)
    real_issues = len([issue for issue in analyzed_issues if issue.is_issue])
    
    # 심각도별 분류
    severity_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for issue in analyzed_issues:
        if issue.is_issue:
            severity_counts[issue.severity_level] += 1
    
    # 카테고리별 분류
    category_counts = {}
    for issue in analyzed_issues:
        if issue.is_issue:
            category = issue.issue_category
            category_counts[category] = category_counts.get(category, 0) + 1
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "query": state.get("query", "Unknown"),
        "total_search_results": len(get_search_results(state)) + len(get_detailed_results(state)),
        "keywords_count": len(get_keywords(state)),
        "total_analyses": total_issues,
        "real_issues_count": real_issues,
        "severity_distribution": severity_counts,
        "category_distribution": category_counts,
        "errors_count": len(state.get("error_messages", []))
    }
    
    return summary
