"""
02_data_model.md에 정의된 데이터 모델에 따른 상태 정의
"""

from __future__ import annotations

from typing import Annotated, TypedDict, List, Optional
from langgraph.graph.message import add_messages

from agents.management.modules.models import SearchResult, IssueAnalysis


class ManagementState(TypedDict):
    """
    인플루언서 이슈 관리 Workflow의 상태를 정의하는 TypedDict 클래스

    02_data_model.md 섹션 1.1에 정의된 구조를 따릅니다.
    아이유를 레퍼런스로 한 인플루언서 이슈 자료 수집을 위한 상태 정보를 정의합니다.
    """

    # 입력 데이터
    query: str                          # 초기 검색 쿼리 (기본값: "아이유")
    
    # 처리 단계별 결과
    initial_search_results: Optional[List[SearchResult]] = None     # 1차 검색 결과 목록
    extracted_keywords: Optional[List[str]] = None                  # LLM이 추출한 키워드 목록
    detailed_search_results: Optional[List[SearchResult]] = None    # 2차 세부 검색 결과 목록
    analyzed_issues: Optional[List[IssueAnalysis]] = None           # LLM 분석된 이슈 목록
    
    # 응답 및 에러
    response: Annotated[list, add_messages]                         # LangGraph 응답 메시지
    error_messages: Optional[List[str]] = None                      # 에러 메시지 목록
