"""
LangGraph Command 객체 활용 함수 기반 노드 모듈

상태 업데이트와 제어 플로우를 통합한 4개 핵심 노드:
- initial_search_node: 초기 포괄적 검색 + 동적 라우팅
- keyword_extraction_node: LLM 기반 키워드 추출 + 조건부 라우팅
- detailed_search_node: 키워드별 세부 검색 + 결과 기반 라우팅
- issue_analysis_node: LLM 기반 이슈 분석 + 심각도별 라우팅

LangGraph Command 패턴으로 노드에서 직접 다음 단계를 결정합니다.
"""

from typing import List, Dict, Any, Literal
from langgraph.graph import END
from langgraph.types import Command

from agents.management.modules.state import ManagementState
from agents.management.modules.models import (
    SearchResult, 
    IssueAnalysis,
    TavilySearchError,
    KeywordExtractionError,
    IssueAnalysisError,
    LLMResponseError
)
from agents.management.modules.tools import (
    search_influencer_initial, 
    search_influencer_detailed,
    safe_search_call
)
from agents.management.modules.chains import (
    safe_keyword_extraction,
    safe_issue_analysis
)
from agents.management.modules.utils import validate_query


def initial_search_node(state: ManagementState) -> Command[Literal["keyword_extraction", "retry_initial_search", "fallback_keywords"]]:
    """
    초기 포괄적 검색 노드 (Command 객체 활용)
    
    검색 결과에 따라 자동으로 다음 단계를 결정합니다:
    - 성공 (3개 이상): keyword_extraction
    - 실패/치명적 에러: retry_initial_search  
    - 부족한 결과: fallback_keywords
    
    Args:
        state: ManagementState 객체
        
    Returns:
        Command: 상태 업데이트 + 라우팅 정보
    """
    try:
        print(f"\n🔍 === 초기검색노드 시작 ===")
        
        # 1. 입력 검증
        query = state.get("query", "")
        if not validate_query(query):
            error_msg = f"유효하지 않은 검색 쿼리: '{query}'"
            print(f"❌ {error_msg}")
            
            return Command(
                update={"error_messages": state.get("error_messages", []) + [error_msg]},
                goto="retry_initial_search"  # 검증 실패 시 재시도
            )
        
        print(f"📝 검색 쿼리: '{query}'")
        
        # 2. 안전한 검색 실행
        search_results = safe_search_call(search_influencer_initial, query)
        
        if not search_results:
            warning_msg = "초기 검색에서 결과를 찾을 수 없습니다."
            print(f"⚠️ {warning_msg}")
            
            return Command(
                update={
                    "error_messages": state.get("error_messages", []) + [warning_msg],
                    "initial_search_results": []
                },
                goto="fallback_keywords"  # 결과 없으면 기본 키워드 사용
            )
        
        # 3. 결과 품질 평가 및 라우팅 결정
        if len(search_results) >= 5:
            print(f"✅ 초기 검색 성공: {len(search_results)}개 결과 → 키워드 추출")
            return Command(
                update={"initial_search_results": search_results},
                goto="keyword_extraction"  # 충분한 결과로 정상 진행
            )
        elif len(search_results) >= 2:
            print(f"⚠️ 초기 검색 부족: {len(search_results)}개 결과 → 기본 키워드 병행")
            return Command(
                update={"initial_search_results": search_results},
                goto="fallback_keywords"  # 부족한 결과로 대체 키워드 사용
            )
        else:
            print(f"❌ 초기 검색 실패: {len(search_results)}개 결과 → 재시도")
            return Command(
                update={"initial_search_results": search_results},
                goto="retry_initial_search"  # 너무 적으면 재시도
            )
        
    except Exception as e:
        error_msg = f"초기 검색 노드에서 치명적 오류: {str(e)}"
        print(f"💥 {error_msg}")
        
        return Command(
            update={
                "error_messages": state.get("error_messages", []) + [error_msg],
                "initial_search_results": []
            },
            goto="retry_initial_search"  # 예외 발생 시 재시도
        )


def keyword_extraction_node(state: ManagementState) -> Command[Literal["detailed_search", "retry_keyword_extraction", "use_default_keywords"]]:
    """
    키워드 추출 노드 (Command 객체 활용)
    
    키워드 추출 결과에 따라 자동으로 다음 단계를 결정합니다:
    - 성공 (3개 이상): detailed_search
    - LLM 에러/부족: retry_keyword_extraction
    - 재시도 한계: use_default_keywords
    
    Args:
        state: ManagementState 객체
        
    Returns:
        Command: 상태 업데이트 + 라우팅 정보
    """
    try:
        print(f"\n🔑 === 키워드추출노드 시작 ===")
        
        # 1. 입력 검증
        search_results = state.get("initial_search_results", [])
        if not search_results:
            error_msg = "키워드 추출을 위한 검색 결과가 없습니다."
            print(f"❌ {error_msg}")
            
            return Command(
                update={
                    "error_messages": state.get("error_messages", []) + [error_msg],
                    "extracted_keywords": []
                },
                goto="use_default_keywords"  # 입력 없으면 기본 키워드
            )
        
        print(f"📊 분석 대상: {len(search_results)}개 검색 결과")
        
        # 2. 재시도 횟수 확인
        extraction_attempts = state.get("extraction_attempts", 0)
        
        # 3. 안전한 키워드 추출
        target_count = 8
        keywords = safe_keyword_extraction(search_results, target_count)
        
        if keywords and len(keywords) >= 5:
            print(f"✅ 키워드 추출 성공: {len(keywords)}개 → 세부 검색")
            print(f"📝 추출된 키워드: {', '.join(keywords)}")
            
            return Command(
                update={"extracted_keywords": keywords},
                goto="detailed_search"  # 성공적 추출로 다음 단계
            )
        
        elif keywords and len(keywords) >= 3:
            print(f"⚠️ 키워드 부족하지만 진행: {len(keywords)}개 → 기본 키워드 추가")
            
            return Command(
                update={"extracted_keywords": keywords},
                goto="use_default_keywords"  # 부족하지만 보완해서 진행
            )
        
        elif extraction_attempts < 2:
            print(f"🔄 키워드 추출 재시도 ({extraction_attempts + 1}/2)")
            
            return Command(
                update={"extraction_attempts": extraction_attempts + 1},
                goto="retry_keyword_extraction"  # 재시도
            )
        
        else:
            warning_msg = f"키워드 추출 최대 재시도 초과. 기본 키워드를 사용합니다."
            print(f"⚠️ {warning_msg}")
            
            return Command(
                update={
                    "error_messages": state.get("error_messages", []) + [warning_msg],
                    "extracted_keywords": []
                },
                goto="use_default_keywords"  # 재시도 한계로 기본 키워드
            )
        
    except Exception as e:
        error_msg = f"키워드 추출 노드에서 예상치 못한 오류: {str(e)}"
        print(f"❌ {error_msg}")
        
        return Command(
            update={
                "error_messages": state.get("error_messages", []) + [error_msg],
                "extracted_keywords": []
            },
            goto="use_default_keywords"  # 예외 발생 시 기본 키워드
        )


def detailed_search_node(state: ManagementState) -> Command[Literal["issue_analysis", "parallel_search", "skip_to_finalize"]]:
    """
    세부 검색 노드 (Command 객체 활용)
    
    키워드 수와 검색 결과에 따라 자동으로 다음 단계를 결정합니다:
    - 다량 키워드 (8개 이상): parallel_search
    - 정상 결과: issue_analysis
    - 결과 없음: skip_to_finalize
    
    Args:
        state: ManagementState 객체
        
    Returns:
        Command: 상태 업데이트 + 라우팅 정보
    """
    try:
        print(f"\n🔎 === 세부검색노드 시작 ===")
        
        # 1. 입력 검증
        keywords = state.get("extracted_keywords", [])
        query = state.get("query", "")
        
        if not keywords:
            error_msg = "세부 검색을 위한 키워드가 없습니다."
            print(f"❌ {error_msg}")
            
            return Command(
                update={
                    "error_messages": state.get("error_messages", []) + [error_msg],
                    "detailed_search_results": []
                },
                goto="skip_to_finalize"  # 키워드 없으면 바로 마무리
            )
        
        if not validate_query(query):
            error_msg = f"유효하지 않은 기본 쿼리: '{query}'"
            print(f"❌ {error_msg}")
            
            return Command(
                update={
                    "error_messages": state.get("error_messages", []) + [error_msg],
                    "detailed_search_results": []
                },
                goto="skip_to_finalize"  # 쿼리 문제로 바로 마무리
            )
        
        print(f"🔍 키워드 기반 세부 검색: {len(keywords)}개 키워드")
        print(f"📝 키워드 목록: {', '.join(keywords)}")
        
        # 2. 키워드 수에 따른 처리 방식 결정
        if len(keywords) > 10:
            print(f"🚀 다량 키워드 ({len(keywords)}개) → 병렬 처리 모드")
            return Command(
                update={"processing_mode": "parallel", "pending_keywords": keywords},
                goto="parallel_search"  # 병렬 처리로 라우팅
            )
        
        # 3. 순차적 키워드 검색 실행
        all_detailed_results = []
        successful_searches = 0
        
        for i, keyword in enumerate(keywords, 1):
            print(f"   [{i}/{len(keywords)}] '{keyword}' 검색 중...")
            
            try:
                # 키워드와 원래 쿼리를 분리해서 전달
                results = safe_search_call(search_influencer_detailed, keyword, query)
                
                if results:
                    all_detailed_results.extend(results)
                    successful_searches += 1
                    print(f"      ✅ {len(results)}개 결과 발견")
                else:
                    print(f"      ⚠️ 결과 없음")
                    
            except Exception as e:
                print(f"      ❌ 검색 실패: {e}")
                continue
        
        # 4. 결과 정리 및 중복 제거
        unique_results = []
        seen_urls = set()
        
        for result in all_detailed_results:
            if result.url not in seen_urls:
                unique_results.append(result)
                seen_urls.add(result.url)
        
        print(f"✅ 세부 검색 완료:")
        print(f"   📊 성공한 키워드 검색: {successful_searches}/{len(keywords)}")
        print(f"   📋 총 발견 결과: {len(all_detailed_results)}개")
        print(f"   🔗 중복 제거 후: {len(unique_results)}개")
        
        # 5. 결과에 따른 라우팅 결정
        if len(unique_results) >= 5:
            print(f"🎯 충분한 검색 결과 → 이슈 분석 진행")
            return Command(
                update={"detailed_search_results": unique_results},
                goto="issue_analysis"  # 충분한 결과로 이슈 분석
            )
        elif len(unique_results) >= 2:
            print(f"⚠️ 제한적 검색 결과 → 이슈 분석 진행")
            return Command(
                update={"detailed_search_results": unique_results},
                goto="issue_analysis"  # 최소한의 결과로 이슈 분석
            )
        else:
            print(f"❌ 검색 결과 부족 → 바로 마무리")
            return Command(
                update={"detailed_search_results": unique_results},
                goto="skip_to_finalize"  # 결과 부족으로 바로 마무리
            )
        
    except Exception as e:
        error_msg = f"세부 검색 노드에서 예상치 못한 오류: {str(e)}"
        print(f"❌ {error_msg}")
        
        return Command(
            update={
                "error_messages": state.get("error_messages", []) + [error_msg],
                "detailed_search_results": []
            },
            goto="skip_to_finalize"  # 예외 발생 시 바로 마무리
        )


def issue_analysis_node(state: ManagementState) -> Command[Literal["finalize", "escalate_issues", "detailed_analysis", END]]:
    """
    이슈 분석 노드 (Command 객체 활용)
    
    이슈 분석 결과와 심각도에 따라 자동으로 다음 단계를 결정합니다:
    - 심각한 이슈 다수 (3개 이상): escalate_issues
    - 정상 이슈: finalize
    - 복잡한 분석 필요: detailed_analysis
    - 이슈 없음: END
    
    Args:
        state: ManagementState 객체
        
    Returns:
        Command: 상태 업데이트 + 라우팅 정보
    """
    try:
        print(f"\n📊 === 이슈분석노드 시작 ===")
        
        # 1. 입력 검증
        search_results = state.get("detailed_search_results", [])
        if not search_results:
            error_msg = "이슈 분석을 위한 검색 결과가 없습니다."
            print(f"❌ {error_msg}")
            
            return Command(
                update={
                    "error_messages": state.get("error_messages", []) + [error_msg],
                    "analyzed_issues": []
                },
                goto=END  # 분석할 결과가 없으면 종료
            )
        
        print(f"🔍 분석 대상: {len(search_results)}개 검색 결과")
        
        # 2. 개별 결과 분석
        analyzed_issues = []
        successful_analyses = 0
        failed_analyses = 0
        high_severity_issues = []
        
        for i, search_result in enumerate(search_results, 1):
            print(f"   [{i}/{len(search_results)}] '{search_result.title[:40]}...' 분석 중")
            
            try:
                # 안전한 이슈 분석
                issue_analysis = safe_issue_analysis(search_result)
                analyzed_issues.append(issue_analysis)
                
                if issue_analysis.is_issue:
                    print(f"      🚨 이슈 발견: {issue_analysis.issue_category} (심각도: {issue_analysis.severity_level})")
                    
                    # 심각한 이슈 추적
                    if issue_analysis.severity_level >= 3:
                        high_severity_issues.append(issue_analysis)
                        
                    successful_analyses += 1
                else:
                    print(f"      ✅ 이슈 없음 (신뢰도: {issue_analysis.confidence_score:.2f})")
                    successful_analyses += 1
                    
            except Exception as e:
                print(f"      ❌ 분석 실패: {e}")
                failed_analyses += 1
                continue
        
        # 3. 분석 결과 요약 및 라우팅 결정
        real_issues = [analysis for analysis in analyzed_issues if analysis.is_issue]
        
        print(f"✅ 이슈 분석 완료:")
        print(f"   📊 성공한 분석: {successful_analyses}/{len(search_results)}")
        print(f"   🚨 실제 이슈 건수: {len(real_issues)}")
        print(f"   🔥 심각한 이슈: {len(high_severity_issues)}")
        print(f"   ❌ 실패한 분석: {failed_analyses}")
        
        # 4. 심각도별 분포 계산
        severity_dist = {}
        category_dist = {}
        
        for issue in real_issues:
            severity = issue.severity_level
            severity_dist[severity] = severity_dist.get(severity, 0) + 1
            
            category = issue.issue_category
            category_dist[category] = category_dist.get(category, 0) + 1
        
        if real_issues:
            print(f"   📈 심각도 분포: {severity_dist}")
            print(f"   📊 카테고리 분포: {category_dist}")
        
        # 5. 라우팅 결정
        if len(high_severity_issues) >= 3:
            print(f"🚨 심각한 이슈 다수 발견 → 에스컬레이션 처리")
            return Command(
                update={
                    "analyzed_issues": analyzed_issues,
                    "alert_level": "critical",
                    "high_severity_count": len(high_severity_issues)
                },
                goto="escalate_issues"  # 심각한 이슈 전용 처리
            )
        
        elif len(real_issues) >= 5 and failed_analyses > len(real_issues) * 0.3:
            print(f"🔍 복잡한 분석 케이스 → 상세 분석 필요")
            return Command(
                update={
                    "analyzed_issues": analyzed_issues,
                    "alert_level": "complex",
                    "failed_analysis_rate": failed_analyses / len(search_results)
                },
                goto="detailed_analysis"  # 추가 분석 필요
            )
        
        elif real_issues:
            print(f"✅ 정상적인 이슈 분석 완료 → 결과 정리")
            return Command(
                update={
                    "analyzed_issues": analyzed_issues,
                    "alert_level": "normal"
                },
                goto="finalize"  # 정상 완료
            )
        
        else:
            print(f"🎉 이슈 없음 → 바로 종료")
            return Command(
                update={
                    "analyzed_issues": analyzed_issues,
                    "alert_level": "none"
                },
                goto=END  # 이슈 없으면 바로 종료
            )
        
    except Exception as e:
        error_msg = f"이슈 분석 노드에서 예상치 못한 오류: {str(e)}"
        print(f"❌ {error_msg}")
        
        return Command(
            update={
                "error_messages": state.get("error_messages", []) + [error_msg],
                "analyzed_issues": []
            },
            goto="finalize"  # 예외 발생 시 안전하게 마무리
        )


# ============================================================================
# 에러 복구 및 특수 처리 노드들 (Command 객체 활용)
# ============================================================================

def retry_initial_search_node(state: ManagementState) -> Command[Literal["keyword_extraction", "fallback_keywords", END]]:
    """
    초기 검색 재시도 노드 (재시도 횟수 관리)
    """
    print("\n🔄 === 초기 검색 재시도 ===")
    
    # 재시도 횟수 추적
    retry_count = state.get("initial_search_retry_count", 0) + 1
    
    if retry_count > 2:  # 최대 재시도 초과
        print(f"❌ 최대 재시도 초과 ({retry_count}/2) → 기본 키워드 사용")
        return Command(
            update={
                "initial_search_retry_count": retry_count,
                "error_messages": state.get("error_messages", []) + ["초기 검색 최대 재시도 초과"]
            },
            goto="fallback_keywords"  # 재시도 한계로 대체 방법
        )
    
    print(f"🔄 재시도 {retry_count}/2 시도 중...")
    
    # 이전 에러 메시지 정리
    clean_errors = [msg for msg in state.get("error_messages", []) if "치명적" not in msg]
    
    # 재시도 실행
    query = state.get("query", "")
    search_results = safe_search_call(search_influencer_initial, query)
    
    if search_results and len(search_results) >= 2:
        print(f"✅ 재시도 성공: {len(search_results)}개 결과 → 키워드 추출")
        return Command(
            update={
                "initial_search_results": search_results,
                "initial_search_retry_count": retry_count,
                "error_messages": clean_errors
            },
            goto="keyword_extraction"  # 성공시 다음 단계로
        )
    else:
        print(f"⚠️ 재시도 실패 → 기본 키워드 사용")
        return Command(
            update={
                "initial_search_results": search_results or [],
                "initial_search_retry_count": retry_count
            },
            goto="fallback_keywords"  # 실패시 대체 방법으로
        )


def retry_keyword_extraction_node(state: ManagementState) -> Command[Literal["detailed_search", "use_default_keywords"]]:
    """
    키워드 추출 재시도 노드
    """
    print("\n🔄 === 키워드 추출 재시도 ===")
    
    # 이전 에러 메시지 정리
    clean_errors = [msg for msg in state.get("error_messages", []) if not any(
        keyword in msg for keyword in ["LLM", "키워드 추출", "JSON"]
    )]
    
    # 재시도 실행
    search_results = state.get("initial_search_results", [])
    keywords = safe_keyword_extraction(search_results, 6)  # 목표 개수 줄임
    
    if keywords and len(keywords) >= 3:
        print(f"✅ 재시도 성공: {len(keywords)}개 키워드 → 세부 검색")
        return Command(
            update={
                "extracted_keywords": keywords,
                "error_messages": clean_errors
            },
            goto="detailed_search"
        )
    else:
        print(f"❌ 재시도 실패 → 기본 키워드 사용")
        return Command(
            update={"error_messages": clean_errors},
            goto="use_default_keywords"
        )


# 기존 함수들은 유지하되 디버깅용
def get_node_execution_summary(state: ManagementState) -> Dict[str, Any]:
    """
    노드 실행 결과 요약 정보를 반환합니다.
    
    Args:
        state: ManagementState 객체
        
    Returns:
        Dict: 실행 요약 정보
    """
    summary = {
        "query": state.get("query", ""),
        "initial_results_count": len(state.get("initial_search_results", [])),
        "keywords_count": len(state.get("extracted_keywords", [])),
        "detailed_results_count": len(state.get("detailed_search_results", [])),
        "analyzed_issues_count": len(state.get("analyzed_issues", [])),
        "real_issues_count": len([a for a in state.get("analyzed_issues", []) if a.is_issue]),
        "error_count": len(state.get("error_messages", [])),
        "has_errors": bool(state.get("error_messages", [])),
        "alert_level": state.get("alert_level", "unknown"),
        "retry_counts": {
            "initial_search": state.get("initial_search_retry_count", 0),
            "keyword_extraction": state.get("extraction_attempts", 0)
        }
    }
    
    return summary
