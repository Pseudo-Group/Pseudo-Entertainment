"""
03_API_specification.md 기반 인플루언서 이슈 자료 수집을 위한 도구(Tools) 모듈

Tavily Search를 활용한 신뢰할 수 있는 최신 정보 수집을 제공합니다.
SearchResult 모델을 반환하며, 체계적인 에러 처리를 포함합니다.
"""

from typing import List
from langchain_community.tools.tavily_search import TavilySearchResults

from agents.management.modules.models import (
    SearchResult, 
    TavilySearchError,
    LLMResponseError
)
from agents.management.modules.utils import convert_tavily_to_search_result, validate_search_result


class TavilySearchTool:
    """
    03_API_specification.md 기반 Tavily Search Tool 래퍼 클래스
    
    개선된 설정과 에러 처리를 포함하며 SearchResult 모델을 반환합니다.
    """
    
    def __init__(
        self, 
        max_results: int = 20,
        include_answer: bool = False,
        include_raw_content: bool = True,
        include_images: bool = False,
        search_depth: str = "basic"
    ):
        """
        03_API_specification.md 섹션 1.1에 정의된 매개변수 사용
        
        Args:
            max_results: 최대 검색 결과 수 (기본값: 20)
            include_answer: AI 생성 답변 포함 여부 (기본값: False)
            include_raw_content: 원본 내용 포함 여부 (기본값: True)
            include_images: 이미지 포함 여부 (기본값: False)
            search_depth: 검색 깊이 "basic" 또는 "advanced" (기본값: "basic")
        """
        self.max_results = max_results
        self.include_raw_content = include_raw_content
        
        try:
            self.search_tool = TavilySearchResults(
                max_results=max_results,
                include_answer=include_answer,
                include_raw_content=include_raw_content,
                include_images=include_images,
                search_depth=search_depth
            )
            print(f"✅ Tavily Search Tool 초기화 완료")
            print(f"   📊 설정: max_results={max_results}, raw_content={include_raw_content}")
            
        except Exception as e:
            raise TavilySearchError(f"Tavily Search Tool 초기화 실패: {str(e)}")
    
    def search(self, query: str) -> List[SearchResult]:
        """
        검색 실행 (03_API_specification.md 섹션 2.1 기반)
        
        Args:
            query: 검색 쿼리
            
        Returns:
            List[SearchResult]: SearchResult 객체 목록
            
        Raises:
            TavilySearchError: 검색 실패 시
        """
        try:
            print(f"🔍 Tavily 검색 실행: '{query}'")
            
            # LangChain Tavily Tool 호출
            raw_results = self.search_tool.invoke({"query": query})
            
            # 결과가 리스트가 아닌 경우 처리
            if not isinstance(raw_results, list):
                raise TavilySearchError(f"예상치 못한 Tavily 응답 형태: {type(raw_results)}")
            
            print(f"📋 Tavily 원본 응답: {len(raw_results)}개 결과")
            
            # SearchResult 객체로 변환
            search_results = []
            for i, raw_result in enumerate(raw_results, 1):
                try:
                    search_result = self._convert_to_search_result(raw_result)
                    
                    # 유효성 검증
                    if validate_search_result(search_result):
                        search_results.append(search_result)
                        print(f"   ✅ 결과 {i}: {search_result.title[:50]}... (점수: {search_result.relevance_score:.2f})")
                    else:
                        print(f"   ⚠️ 결과 {i}: 유효하지 않아 스킵 - {search_result.url}")
                        
                except Exception as e:
                    print(f"   ❌ 결과 {i}: 변환 실패 - {e}")
                    continue
            
            print(f"✅ 최종 변환 완료: {len(search_results)}개 SearchResult")
            return search_results
            
        except TavilySearchError:
            # 이미 TavilySearchError인 경우 재발생
            raise
        except Exception as e:
            # 기타 예외를 TavilySearchError로 래핑
            raise TavilySearchError(f"검색 실패: {str(e)}")
    
    def _convert_to_search_result(self, raw_result: dict) -> SearchResult:
        """
        Tavily 응답을 SearchResult로 변환 (03_API_specification.md 섹션 2.1)
        
        Args:
            raw_result: Tavily 원본 응답 딕셔너리
            
        Returns:
            SearchResult: 변환된 SearchResult 객체
        """
        # 기본 convert_tavily_to_search_result 사용 후 raw_content 추가
        search_result = convert_tavily_to_search_result(raw_result)
        
        # raw_content 추가 (03_API_specification.md 추가 필드)
        if self.include_raw_content and "raw_content" in raw_result:
            search_result.raw_content = raw_result["raw_content"]
        
        return search_result
    
    def initial_search(self, query: str) -> List[SearchResult]:
        """
        인플루언서에 대한 초기 포괄적 검색을 수행합니다.
        
        Args:
            query: 검색 쿼리 (예: "아이유")
            
        Returns:
            List[SearchResult]: 검색 결과 목록
        """
        search_query = f"{query} 최신 이슈 논란 뉴스"
        return self.search(search_query)
    
    def detailed_search(self, keyword: str, base_query: str) -> List[SearchResult]:
        """
        특정 키워드와 기본 쿼리를 결합한 세부 검색을 수행합니다.
        
        Args:
            keyword: 검색할 키워드
            base_query: 기본 쿼리 (예: "아이유")
            
        Returns:
            List[SearchResult]: 검색 결과 목록
        """
        search_query = f"{base_query} {keyword} 상세정보 분석"
        results = self.search(search_query)
        
        # 키워드 정보 추가 (추적을 위해)
        for result in results:
            result.content = f"[키워드: {keyword}] {result.content}"
        
        return results


# 전역 검색 도구 인스턴스 (03_API_specification.md 설정 사용)
search_tool = TavilySearchTool(
    max_results=20,
    include_answer=False,
    include_raw_content=True,
    include_images=False,
    search_depth="basic"
)


def search_influencer_initial(query: str) -> List[SearchResult]:
    """
    인플루언서 초기 검색 함수 (03_API_specification.md 기반)
    
    Args:
        query: 검색할 쿼리 (예: "아이유")
        
    Returns:
        List[SearchResult]: SearchResult 객체 목록
        
    Raises:
        TavilySearchError: 검색 실패 시
    """
    try:
        return search_tool.initial_search(query)
    except Exception as e:
        if not isinstance(e, TavilySearchError):
            raise TavilySearchError(f"초기 검색 실패: {str(e)}")
        raise


def search_influencer_detailed(keyword: str, base_query: str) -> List[SearchResult]:
    """
    인플루언서 키워드별 세부 검색 함수 (03_API_specification.md 기반)
    
    Args:
        keyword: 검색할 키워드
        base_query: 기본 쿼리 (예: "아이유")
        
    Returns:
        List[SearchResult]: SearchResult 객체 목록
        
    Raises:
        TavilySearchError: 검색 실패 시
    """
    try:
        return search_tool.detailed_search(keyword, base_query)
    except Exception as e:
        if not isinstance(e, TavilySearchError):
            raise TavilySearchError(f"세부 검색 실패 (키워드: {keyword}): {str(e)}")
        raise


# 도구 목록
TOOLS = [search_influencer_initial, search_influencer_detailed]


# 03_API_specification.md 섹션 3.2: 안전한 API 호출
def safe_search_call(search_function, *args, **kwargs):
    """
    안전한 검색 API 호출
    
    Args:
        search_function: 호출할 검색 함수
        *args, **kwargs: 전달할 인자들
        
    Returns:
        검색 결과 또는 빈 리스트 (실패 시)
    """
    try:
        return search_function(*args, **kwargs)
    except TavilySearchError as e:
        print(f"🔍 검색 API 호출 실패: {e}")
        return []
    except Exception as e:
        print(f"🔍 예상치 못한 검색 오류: {e}")
        return []
