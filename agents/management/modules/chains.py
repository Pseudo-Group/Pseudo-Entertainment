"""
03_API_specification.md 기반 인플루언서 이슈 분석을 위한 체인(Chains) 모듈

LLM과 프롬프트를 결합하여 키워드 추출 및 이슈 분석 체인을 구성합니다.
JSON response_format을 사용하여 구조화된 응답을 보장합니다.
"""

import json
from typing import List

from agents.management.modules.models import (
    get_openai_model,
    SearchResult,
    IssueAnalysis,
    KeywordExtractionError,
    IssueAnalysisError,
    LLMResponseError
)
from agents.management.modules.prompts import (
    get_keyword_extraction_prompt,
    get_issue_analysis_prompt
)
from agents.management.modules.utils import (
    validate_query, 
    convert_llm_to_issue_analysis,
    clean_text_simple,
    clean_keywords_simple
)


class KeywordExtractionChain:
    """
    03_API_specification.md 섹션 2.2 기반 키워드 추출 체인
    JSON response_format을 사용하여 구조화된 키워드 추출을 수행합니다.
    """
    
    def __init__(self):
        """체인 초기화 - JSON 출력 강제"""
        self.model = get_openai_model(
            temperature=0.3,  # 일관성을 위해 낮은 온도
            response_format={"type": "json_object"}  # JSON 출력 강제
        )
        self.prompt = get_keyword_extraction_prompt()
        print("✅ KeywordExtractionChain 초기화 완료 (JSON mode)")
    
    def extract_keywords(
        self, 
        search_results: List[SearchResult],
        target_count: int = 8
    ) -> List[str]:
        """
        키워드 추출 실행 (03_API_specification.md 기반)
        
        Args:
            search_results: SearchResult 객체 목록
            target_count: 목표 키워드 개수 (기본값: 8)
            
        Returns:
            List[str]: 추출된 키워드 목록
            
        Raises:
            KeywordExtractionError: 키워드 추출 실패 시
        """
        try:
            if not search_results:
                raise KeywordExtractionError("검색 결과가 없어 키워드를 추출할 수 없습니다.")
            
            print(f"🔑 {len(search_results)}개 SearchResult에서 키워드 추출 시작...")
            
            # 검색 결과를 텍스트로 결합
            combined_text = self._combine_search_results(search_results)
            
            # 체인 실행
            chain = self.prompt | self.model
            response = chain.invoke({
                "search_results_formatted": combined_text,
                "target_count": target_count
            })
            
            # JSON 응답 파싱
            response_text = response.content if hasattr(response, 'content') else str(response)
            result_data = json.loads(response_text)
            
            keywords = result_data.get("keywords", [])
            reasoning = result_data.get("reasoning", "")
            
            # 결과 검증
            if not keywords:
                raise KeywordExtractionError("LLM이 키워드를 반환하지 않았습니다.")
            
            # 목표 개수로 제한
            keywords = keywords[:target_count]
            
            print(f"✅ 키워드 추출 완료: {len(keywords)}개")
            print(f"📝 추출 근거: {reasoning[:100]}...")
            
            return keywords
            
        except json.JSONDecodeError as e:
            raise LLMResponseError(f"LLM JSON 응답 파싱 실패: {e}")
        except KeywordExtractionError:
            # 이미 KeywordExtractionError인 경우 재발생
            raise
        except Exception as e:
            raise KeywordExtractionError(f"키워드 추출 중 오류 발생: {e}")
    
    def _combine_search_results(self, search_results: List[SearchResult]) -> str:
        """SearchResult 목록을 텍스트로 결합 (05_workflow_and_process.md 텍스트 정리 적용)"""
        combined_text = ""
        for i, result in enumerate(search_results[:5], 1):  # 상위 5개만 사용
            combined_text += f"[결과 {i}]\n"
            combined_text += f"제목: {result.title}\n"
            combined_text += f"내용: {result.content[:300]}...\n"
            combined_text += f"출처: {result.source}\n\n"
        
        # 05_workflow_and_process.md 섹션 4.2.1 텍스트 정리 적용
        return clean_text_simple(combined_text, max_length=8000)


class IssueAnalysisChain:
    """
    03_API_specification.md 섹션 2.2 기반 이슈 분석 체인
    JSON response_format을 사용하여 구조화된 이슈 분석을 수행합니다.
    """
    
    def __init__(self):
        """체인 초기화 - JSON 출력 강제"""
        self.model = get_openai_model(
            temperature=0.1,  # 분석의 일관성을 위해 낮은 온도
            response_format={"type": "json_object"}  # JSON 출력 강제
        )
        self.prompt = get_issue_analysis_prompt()
        print("✅ IssueAnalysisChain 초기화 완료 (JSON mode)")
    
    def analyze_issue(self, search_result: SearchResult) -> IssueAnalysis:
        """
        이슈 분석 실행 (03_API_specification.md 기반)
        
        Args:
            search_result: 분석할 SearchResult 객체
            
        Returns:
            IssueAnalysis: 분석 결과 객체
            
        Raises:
            IssueAnalysisError: 이슈 분석 실패 시
        """
        try:
            print(f"📊 이슈 분석 시작: {search_result.title[:50]}...")
            
            # 체인 실행
            chain = self.prompt | self.model
            response = chain.invoke({
                "title": search_result.title,
                "content": search_result.content,
                "source": search_result.source,
                "published_date": search_result.published_date,
                "url": search_result.url,
                "relevance_score": search_result.relevance_score
            })
            
            # JSON 응답 파싱
            response_text = response.content if hasattr(response, 'content') else str(response)
            result_data = json.loads(response_text)
            
            # IssueAnalysis 객체 생성
            issue_analysis = IssueAnalysis(
                original_result=search_result,
                is_issue=bool(result_data.get("is_issue", False)),
                severity_level=int(result_data.get("severity_level", 1)),
                issue_category=str(result_data.get("issue_category", "기타")),
                summary=str(result_data.get("summary", "")),
                potential_impact=str(result_data.get("potential_impact", "")),
                confidence_score=float(result_data.get("confidence_score", 0.0)),
                analysis_reasoning=str(result_data.get("reasoning", ""))
            )
            
            # 결과 유효성 검증
            self._validate_analysis_result(issue_analysis)
            
            if issue_analysis.is_issue:
                print(f"   🚨 이슈 발견: {issue_analysis.issue_category} (심각도: {issue_analysis.severity_level})")
            else:
                print(f"   ✅ 이슈 없음 (신뢰도: {issue_analysis.confidence_score:.2f})")
            
            return issue_analysis
            
        except json.JSONDecodeError as e:
            raise LLMResponseError(f"LLM JSON 응답 파싱 실패: {e}")
        except (ValueError, TypeError) as e:
            raise LLMResponseError(f"LLM 응답 데이터 타입 오류: {e}")
        except IssueAnalysisError:
            # 이미 IssueAnalysisError인 경우 재발생
            raise
        except Exception as e:
            raise IssueAnalysisError(f"이슈 분석 중 오류 발생: {e}")
    
    def _validate_analysis_result(self, analysis: IssueAnalysis):
        """분석 결과 유효성 검증"""
        valid_categories = ["발언", "행동", "컨텐츠", "개인"]
        
        if not (1 <= analysis.severity_level <= 4):
            raise IssueAnalysisError(f"잘못된 심각도 등급: {analysis.severity_level}")
        
        if analysis.issue_category not in valid_categories:
            raise IssueAnalysisError(f"잘못된 이슈 카테고리: {analysis.issue_category}")
        
        if not (0.0 <= analysis.confidence_score <= 1.0):
            raise IssueAnalysisError(f"잘못된 신뢰도 점수: {analysis.confidence_score}")


# 전역 체인 인스턴스들
_keyword_chain = None
_analysis_chain = None


def create_keyword_extraction_chain():
    """
    키워드 추출을 위한 체인을 생성합니다 (싱글톤 패턴)
    
    Returns:
        KeywordExtractionChain: 키워드 추출 체인
    """
    global _keyword_chain
    if _keyword_chain is None:
        _keyword_chain = KeywordExtractionChain()
    return _keyword_chain


def create_issue_analysis_chain():
    """
    이슈 분석을 위한 체인을 생성합니다 (싱글톤 패턴)

    Returns:
        IssueAnalysisChain: 이슈 분석 체인
    """
    global _analysis_chain
    if _analysis_chain is None:
        _analysis_chain = IssueAnalysisChain()
    return _analysis_chain


# 03_API_specification.md 섹션 3.2: 안전한 API 호출
def safe_keyword_extraction(search_results: List[SearchResult], target_count: int = 8) -> List[str]:
    """
    안전한 키워드 추출 (05_workflow_and_process.md 키워드 정리 적용)
    
    Args:
        search_results: SearchResult 목록
        target_count: 목표 키워드 개수

    Returns:
        List[str]: 키워드 목록 (실패 시 빈 리스트)
    """
    try:
        chain = create_keyword_extraction_chain()
        raw_keywords = chain.extract_keywords(search_results, target_count)
        # 05_workflow_and_process.md 섹션 4.2.2 키워드 정리 적용
        return clean_keywords_simple(raw_keywords)
    except (KeywordExtractionError, LLMResponseError) as e:
        print(f"🔑 키워드 추출 API 호출 실패: {e}")
        return []
    except Exception as e:
        print(f"🔑 예상치 못한 키워드 추출 오류: {e}")
        return []


def safe_issue_analysis(search_result: SearchResult) -> IssueAnalysis:
    """
    안전한 이슈 분석
    
    Args:
        search_result: 분석할 SearchResult
        
    Returns:
        IssueAnalysis: 분석 결과 (실패 시 기본값)
    """
    try:
        chain = create_issue_analysis_chain()
        return chain.analyze_issue(search_result)
    except (IssueAnalysisError, LLMResponseError) as e:
        print(f"📊 이슈 분석 API 호출 실패: {e}")
        # 실패 시 기본 IssueAnalysis 반환
        return IssueAnalysis(
            original_result=search_result,
            is_issue=False,
            severity_level=1,
            issue_category="기타",
            summary="분석 실패",
            potential_impact="분석할 수 없음",
            confidence_score=0.0,
            analysis_reasoning=f"분석 실패: {str(e)}"
        )
    except Exception as e:
        print(f"📊 예상치 못한 이슈 분석 오류: {e}")
        return IssueAnalysis(
            original_result=search_result,
            is_issue=False,
            severity_level=1,
            issue_category="기타",
            summary="분석 실패",
            potential_impact="분석할 수 없음",
            confidence_score=0.0,
            analysis_reasoning=f"예상치 못한 오류: {str(e)}"
    )
