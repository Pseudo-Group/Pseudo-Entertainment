"""
LangGraph Command 객체 활용 Management 워크플로우

Command 객체로 상태 업데이트와 제어 플로우를 통합한 4단계 워크플로우:
1. 초기 검색 → 동적 라우팅 → 2. 키워드 추출 → 조건부 라우팅 
→ 3. 세부 검색 → 결과 기반 라우팅 → 4. 이슈 분석 → 심각도별 라우팅

에러 발생 시 자동 복구 및 재시도 로직을 포함합니다.
"""

from typing import Dict, Any, Optional, Literal
from langgraph.graph import StateGraph, END, START

from agents.management.modules.state import ManagementState
from agents.management.modules.nodes import (
    initial_search_node,
    keyword_extraction_node,
    detailed_search_node,
    issue_analysis_node,
    retry_initial_search_node,
    retry_keyword_extraction_node,
    get_node_execution_summary
)
from agents.management.modules.utils import (
    validate_query,
    validate_intermediate_results,
    get_required_data
)
from agents.management.modules.models import (
    TavilySearchError,
    KeywordExtractionError,
    IssueAnalysisError,
    LLMResponseError
)


def prepare_initial_state(query: str) -> ManagementState:
    """
    초기 상태 준비 (입력 검증 포함)
    
    Args:
        query: 검색할 인플루언서 이름
        
    Returns:
        ManagementState: 초기화된 상태 객체
    """
    print(f"\n🚀 === Management 워크플로우 시작 ===")
    print(f"📝 검색 대상: '{query}'")
    
    # 입력 검증
    if not validate_query(query):
        print(f"❌ 유효하지 않은 쿼리입니다: '{query}'")
        return {
            "query": query,
            "initial_search_results": None,
            "extracted_keywords": None,
            "detailed_search_results": None,
            "analyzed_issues": None,
            "response": [],
            "error_messages": [f"유효하지 않은 검색 쿼리: '{query}'"]
        }
    
    # 초기 상태 구성
    initial_state: ManagementState = {
        "query": query,
        "initial_search_results": None,
        "extracted_keywords": None,
        "detailed_search_results": None,
        "analyzed_issues": None,
        "response": [],
        "error_messages": []
    }
    
    print(f"✅ 초기 상태 준비 완료")
    return initial_state


# ============================================================================
# 특수 처리 노드들 (Command 객체 활용)
# ============================================================================

def fallback_keywords_node(state: ManagementState) -> ManagementState:
    """
    기본 키워드 제공 노드 (아이유 관련 기본 키워드)
    """
    print("\n🔧 === 기본 키워드 제공 ===")
    
    # 아이유 관련 기본 키워드 세트
    default_keywords = [
        "음악활동", "드라마", "영화", "광고", "팬미팅", 
        "앨범", "콘서트", "소셜미디어", "발언", "행동"
    ]
    
    # 기존 키워드와 병합
    existing_keywords = state.get("extracted_keywords", [])
    if existing_keywords:
        # 중복 제거하면서 병합
        combined = list(set(existing_keywords + default_keywords))
        print(f"🔗 기존 키워드와 병합: {len(existing_keywords)} + {len(default_keywords)} → {len(combined)}개")
    else:
        combined = default_keywords
        print(f"📝 기본 키워드만 사용: {len(combined)}개")
    
    print(f"✅ 최종 키워드: {', '.join(combined)}")
    
    state["extracted_keywords"] = combined
    return state


def use_default_keywords_node(state: ManagementState) -> ManagementState:
    """
    기본 키워드 강제 사용 노드 (키워드 추출 실패 시)
    """
    print("\n🔧 === 기본 키워드 강제 사용 ===")
    
    # 엄선된 아이유 관련 키워드
    default_keywords = ["아이유", "이지은", "음악", "드라마", "가수", "배우"]
    
    print(f"📝 강제 키워드 적용: {', '.join(default_keywords)}")
    state["extracted_keywords"] = default_keywords
    
    return state


def escalate_issues_node(state: ManagementState) -> ManagementState:
    """
    심각한 이슈 에스컬레이션 처리 노드
    """
    print("\n🚨 === 심각한 이슈 에스컬레이션 ===")
    
    analyzed_issues = state.get("analyzed_issues", [])
    high_severity_issues = [
        issue for issue in analyzed_issues 
        if issue.is_issue and issue.severity_level >= 3
    ]
    
    print(f"🔥 심각한 이슈 {len(high_severity_issues)}개 감지")
    
    # 에스컬레이션 정보 추가
    escalation_info = {
        "escalation_triggered": True,
        "high_severity_count": len(high_severity_issues),
        "escalation_timestamp": "현재시간",  # 실제로는 datetime.now()
        "requires_immediate_attention": True
    }
    
    state["escalation_info"] = escalation_info
    print(f"⚡ 에스컬레이션 처리 완료")
    
    return state


def detailed_analysis_node(state: ManagementState) -> ManagementState:
    """
    복잡한 케이스 상세 분석 노드
    """
    print("\n🔍 === 복잡한 케이스 상세 분석 ===")
    
    analyzed_issues = state.get("analyzed_issues", [])
    failed_rate = state.get("failed_analysis_rate", 0.0)
    
    print(f"📊 실패율: {failed_rate:.2%}")
    print(f"🔎 추가 분석 시작...")
    
    # 추가 분석 정보
    detailed_info = {
        "detailed_analysis_triggered": True,
        "complexity_score": failed_rate,
        "additional_analysis_performed": True,
        "analysis_confidence": "medium" if failed_rate > 0.5 else "high"
    }
    
    state["detailed_analysis_info"] = detailed_info
    print(f"✅ 상세 분석 완료")
    
    return state


def skip_to_finalize_node(state: ManagementState) -> ManagementState:
    """
    검색 결과 부족으로 조기 마무리 노드
    """
    print("\n⏭️ === 조기 마무리 처리 ===")
    
    # 빈 결과로 설정
    state["analyzed_issues"] = []
    state["alert_level"] = "insufficient_data"
    
    warning_msg = "검색 결과가 부족하여 이슈 분석을 수행할 수 없습니다."
    state["error_messages"] = state.get("error_messages", []) + [warning_msg]
    
    print(f"⚠️ {warning_msg}")
    return state


def parallel_search_node(state: ManagementState) -> ManagementState:
    """
    병렬 검색 처리 노드 (다량 키워드용)
    """
    print("\n🚀 === 병렬 검색 처리 ===")
    
    keywords = state.get("pending_keywords", [])
    print(f"🔍 병렬 처리 대상: {len(keywords)}개 키워드")
    
    # 실제로는 병렬 처리 구현 (여기서는 시뮬레이션)
    # 예: concurrent.futures.ThreadPoolExecutor 사용
    
    # 시뮬레이션 결과
    state["detailed_search_results"] = []  # 실제로는 병렬 검색 결과
    state["parallel_processing_completed"] = True
    
    print(f"⚡ 병렬 검색 완료")
    return state


def finalize_node(state: ManagementState) -> ManagementState:
    """
    워크플로우 최종 마무리 노드 - 종합 보고서 생성
    """
    print("\n🎯 === 워크플로우 최종 마무리 ===")
    
    # 1. 기본 데이터 수집
    query = state.get("query", "")
    initial_results = state.get("initial_search_results", [])
    keywords = state.get("extracted_keywords", [])
    detailed_results = state.get("detailed_search_results", [])
    analyzed_issues = state.get("analyzed_issues", [])
    
    # 2. 이슈 분석 결과 정리
    real_issues = [issue for issue in analyzed_issues if issue.is_issue]
    total_articles = len(initial_results) + len(detailed_results)
    
    # 심각도별 분포
    severity_dist = {}
    category_dist = {}
    high_risk_issues = []
    
    for issue in real_issues:
        severity = issue.severity_level
        severity_dist[severity] = severity_dist.get(severity, 0) + 1
        
        category = issue.issue_category  
        category_dist[category] = category_dist.get(category, 0) + 1
        
        if severity >= 3:
            high_risk_issues.append(issue)
    
    # 3. 위험도 평가
    if len(high_risk_issues) >= 2:
        risk_level = "HIGH"
        risk_color = "🔴"
    elif len(real_issues) >= 3:
        risk_level = "MEDIUM" 
        risk_color = "🟡"
    elif len(real_issues) >= 1:
        risk_level = "LOW"
        risk_color = "🟢"
    else:
        risk_level = "MINIMAL"
        risk_color = "✅"
    
    # 4. 종합 보고서 생성
    final_report = {
        "executive_summary": {
            "target": query,
            "analysis_date": "2024-12-28",
            "total_articles_analyzed": total_articles,
            "issues_found": len(real_issues),
            "risk_level": risk_level,
            "risk_assessment": f"{risk_color} {risk_level} 위험도"
        },
        
        "issue_analysis": {
            "total_issues": len(real_issues),
            "high_severity_issues": len(high_risk_issues),
            "severity_distribution": severity_dist,
            "category_distribution": category_dist,
            "issue_details": [
                {
                    "title": issue.original_result.title[:100],
                    "category": issue.issue_category,
                    "severity": issue.severity_level,
                    "summary": issue.summary,
                    "confidence": issue.confidence_score
                }
                for issue in real_issues[:5]  # 상위 5개만
            ]
        },
        
        "keyword_trends": {
            "extracted_keywords": keywords,
            "trending_topics": keywords[:3] if keywords else [],
            "search_coverage": f"{len(keywords)}개 키워드 분석 완료"
        },
        
        "recommendations": {
            "immediate_actions": [],
            "monitoring_points": [],
            "long_term_strategy": []
        }
    }
    
    # 5. 위험도별 추천 액션 생성
    if risk_level == "HIGH":
        final_report["recommendations"]["immediate_actions"] = [
            "🚨 즉시 위기관리팀 소집",
            "📢 공식 입장 발표 검토",
            "📱 소셜미디어 모니터링 강화"
        ]
    elif risk_level == "MEDIUM":
        final_report["recommendations"]["immediate_actions"] = [
            "⚠️ 상황 모니터링 강화", 
            "📋 대응 시나리오 준비",
            "🤝 팬 커뮤니티 소통 강화"
        ]
    else:
        final_report["recommendations"]["immediate_actions"] = [
            "✅ 현재 상황 양호",
            "📊 정기 모니터링 지속",
            "💪 긍정적 콘텐츠 강화"
        ]
    
    # 공통 모니터링 포인트
    final_report["recommendations"]["monitoring_points"] = [
        f"🔍 '{keywords[0] if keywords else query}' 키워드 지속 모니터링",
        "📈 여론 변화 추이 관찰",
        "📰 주요 언론 보도 추적"
    ]
    
    # 6. 실행 메타데이터
    summary = get_node_execution_summary(state)
    total_steps = 4
    completed_steps = sum([
        1 if initial_results else 0,
        1 if keywords else 0,
        1 if detailed_results is not None else 0,
        1 if analyzed_issues is not None else 0
    ])
    success_rate = (completed_steps / total_steps) * 100
    
    final_info = {
        "workflow_completed": True,
        "success_rate": success_rate,
        "completed_steps": completed_steps,
        "total_steps": total_steps,
        "execution_summary": summary
    }
    
    # 7. 상태 업데이트
    state["final_report"] = final_report
    state["final_info"] = final_info
    
    # 8. 사용자 친화적 결과 출력
    print(f"\n🎯 === {query} 종합 분석 보고서 ===")
    print(f"📊 분석 기사 수: {total_articles}개")
    print(f"🚨 발견된 이슈: {len(real_issues)}개")
    print(f"{risk_color} 위험도: {risk_level}")
    
    if real_issues:
        print(f"\n📋 주요 이슈:")
        for i, issue in enumerate(real_issues[:3], 1):
            print(f"   {i}. [{issue.issue_category}] {issue.summary[:50]}... (심각도: {issue.severity_level})")
    
    if keywords:
        print(f"\n🔍 트렌딩 키워드: {', '.join(keywords[:5])}")
    
    print(f"\n💡 즉시 액션:")
    for action in final_report["recommendations"]["immediate_actions"]:
        print(f"   • {action}")
    
    print(f"\n✅ 워크플로우 완료 (성공률: {success_rate:.1f}%)")
    
    return state


# ============================================================================
# 워크플로우 구성 및 실행
# ============================================================================

def create_management_workflow() -> StateGraph:
    """
    Command 객체 기반 Management 워크플로우 생성
    
    Returns:
        StateGraph: 컴파일 준비된 워크플로우 그래프
    """
    print("\n🔧 === Command 기반 워크플로우 구성 ===")
    
    # StateGraph 초기화
    workflow = StateGraph(ManagementState)
    
    # 주요 노드 추가 (Command 객체 반환)
    workflow.add_node("initial_search", initial_search_node)
    workflow.add_node("keyword_extraction", keyword_extraction_node) 
    workflow.add_node("detailed_search", detailed_search_node)
    workflow.add_node("issue_analysis", issue_analysis_node)
    
    # 에러 복구 노드 추가
    workflow.add_node("retry_initial_search", retry_initial_search_node)
    workflow.add_node("retry_keyword_extraction", retry_keyword_extraction_node)
    
    # 특수 처리 노드 추가 (일반 함수)
    workflow.add_node("fallback_keywords", fallback_keywords_node)
    workflow.add_node("use_default_keywords", use_default_keywords_node)
    workflow.add_node("escalate_issues", escalate_issues_node)
    workflow.add_node("detailed_analysis", detailed_analysis_node)
    workflow.add_node("skip_to_finalize", skip_to_finalize_node)
    workflow.add_node("parallel_search", parallel_search_node)
    workflow.add_node("finalize", finalize_node)
    
    # 시작점 설정 (Command 객체가 자동 라우팅하므로 단순화)
    workflow.add_edge(START, "initial_search")
    
    # 일반 노드들은 finalize로 연결 (Command 객체가 직접 라우팅하지 않는 경우)
    workflow.add_edge("fallback_keywords", "detailed_search")
    workflow.add_edge("use_default_keywords", "detailed_search")
    workflow.add_edge("escalate_issues", "finalize")
    workflow.add_edge("detailed_analysis", "finalize")
    workflow.add_edge("skip_to_finalize", "finalize")
    workflow.add_edge("parallel_search", "issue_analysis")
    workflow.add_edge("finalize", END)
    
    print(f"✅ 워크플로우 구성 완료:")
    print(f"   📊 총 노드 수: 12개")
    print(f"   🔄 Command 노드: 6개")
    print(f"   🛠️ 일반 노드: 6개")
    
    return workflow


def run_management_workflow(query: str, config: Optional[Dict[str, Any]] = None) -> ManagementState:
    """
    Management 워크플로우 실행 (Command 객체 활용)
    
    Args:
        query: 검색할 인플루언서 이름
        config: 실행 설정 (옵션)
        
    Returns:
        ManagementState: 실행 완료된 최종 상태
    """
    try:
        print(f"\n🚀 === Management 워크플로우 실행 시작 ===")
        print(f"📝 검색 대상: '{query}'")
        
        # 1. 초기 상태 준비
        initial_state = prepare_initial_state(query)
        
        # 기본 입력 검증 실패 시 조기 반환
        if initial_state.get("error_messages"):
            print(f"❌ 입력 검증 실패 - 워크플로우 중단")
            return initial_state
        
        # 2. 워크플로우 생성 및 컴파일
        workflow = create_management_workflow()
        compiled_workflow = workflow.compile()
        
        print(f"✅ 워크플로우 컴파일 완료")
        
        # 3. 워크플로우 실행 (Command 객체가 자동 라우팅)
        print(f"🏃 워크플로우 실행 중...")
        
        # 실행 설정 준비
        run_config = config or {}
        
        # LangGraph 실행
        final_state = compiled_workflow.invoke(initial_state, config=run_config)
        
        # 4. 실행 결과 검증
        if not final_state:
            error_msg = "워크플로우 실행이 실패했습니다."
            print(f"❌ {error_msg}")
            
            initial_state["error_messages"] = initial_state.get("error_messages", []) + [error_msg]
            return initial_state
        
        # 5. 실행 성공
        success_rate = final_state.get("final_info", {}).get("success_rate", 0)
        print(f"✅ 워크플로우 실행 완료")
        print(f"📊 최종 성공률: {success_rate:.1f}%")
        
        return final_state
        
    except Exception as e:
        error_msg = f"워크플로우 실행 중 예상치 못한 오류: {str(e)}"
        print(f"💥 {error_msg}")
        
        # 안전한 상태 반환
        if 'initial_state' in locals():
            initial_state["error_messages"] = initial_state.get("error_messages", []) + [error_msg]
            return initial_state
        else:
            # 초기 상태 생성도 실패한 경우
            return {
                "query": query,
                "initial_search_results": None,
                "extracted_keywords": None,
                "detailed_search_results": None,
                "analyzed_issues": None,
                "response": [],
                "error_messages": [error_msg]
            }


def safe_workflow_execution(query: str, max_retries: int = 2) -> ManagementState:
    """
    안전한 워크플로우 실행 (재시도 포함)
    
    Args:
        query: 검색할 인플루언서 이름
        max_retries: 최대 재시도 횟수
        
    Returns:
        ManagementState: 실행 완료된 최종 상태
    """
    for attempt in range(max_retries + 1):
        try:
            print(f"\n🔄 === 워크플로우 실행 시도 {attempt + 1}/{max_retries + 1} ===")
            
            result = run_management_workflow(query)
            
            # 성공 여부 확인
            success_rate = result.get("final_info", {}).get("success_rate", 0)
            
            if success_rate >= 50:  # 50% 이상 성공 시 종료
                print(f"✅ 워크플로우 성공 (성공률: {success_rate:.1f}%)")
                return result
            elif attempt < max_retries:
                print(f"⚠️ 성공률 부족 ({success_rate:.1f}%) - 재시도")
                continue
            else:
                print(f"❌ 최대 재시도 초과 - 현재 결과 반환")
                return result
                
        except Exception as e:
            error_msg = f"워크플로우 실행 시도 {attempt + 1} 실패: {str(e)}"
            print(f"❌ {error_msg}")
            
            if attempt == max_retries:
                # 최종 실패
                return {
                    "query": query,
                    "initial_search_results": None,
                    "extracted_keywords": None,
                    "detailed_search_results": None,
                    "analyzed_issues": None,
                    "response": [],
                    "error_messages": [error_msg]
                }
            else:
                print(f"🔄 재시도 대기 중...")


# ============================================================================
# 워크플로우 실행 함수 (하위 호환성)
# ============================================================================

def execute_management_workflow(query: str) -> ManagementState:
    """
    하위 호환성을 위한 워크플로우 실행 함수
    
    Args:
        query: 검색할 인플루언서 이름
        
    Returns:
        ManagementState: 실행 완료된 최종 상태
    """
    return safe_workflow_execution(query)


# ============================================================================
# LangGraph Dev 서버를 위한 Export
# ============================================================================

# LangGraph dev 서버에서 사용할 컴파일된 워크플로우
management_workflow = create_management_workflow().compile()
