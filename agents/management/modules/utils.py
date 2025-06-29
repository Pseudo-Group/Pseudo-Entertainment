"""
유틸리티 및 보조 함수 모듈

이 모듈은 Management Workflow에서 사용할 수 있는 다양한 유틸리티 함수를 제공합니다.
인스타그램 컨텐츠 검증, 정책 검색, 위험 요소 분석에 필요한 유틸리티 함수들을 포함합니다.

추후 개발 시 필요한 유틸리티 함수를 이 모듈에 추가하여 코드 재사용성을 높일 수 있습니다.
예를 들어, 텍스트 전처리, 포맷팅, 데이터 변환 등의 기능을 구현할 수 있습니다.
"""

from typing import Any, Dict, List


def format_verification_result(result: Dict[str, Any]) -> str:
    """
    인스타그램 컨텐츠 검증 결과를 포맷팅합니다.

    Args:
        result: 검증 결과 딕셔너리

    Returns:
        str: 포맷팅된 결과 문자열
    """
    if "error" in result:
        return f"오류: {result['error']}"

    status = "승인" if result.get("is_approved", False) else "거부"
    score = result.get("score", 0.0)
    risk_level = result.get("risk_level", "unknown")

    formatted = f"""
인스타그램 컨텐츠 검증 결과:
상태: {status}
점수: {score:.2f}
위험도: {risk_level}

승인/거부 이유:
"""

    for reason in result.get("reasons", []):
        formatted += f"- {reason}\n"

    if result.get("warnings"):
        formatted += "\n경고사항:\n"
        for warning in result["warnings"]:
            formatted += f"- {warning}\n"

    if result.get("suggestions"):
        formatted += "\n개선 제안:\n"
        for suggestion in result["suggestions"]:
            formatted += f"- {suggestion}\n"

    if result.get("policy_references"):
        formatted += "\n참조한 정책:\n"
        for policy in result["policy_references"]:
            formatted += f"- {policy}\n"

    if result.get("similar_cases"):
        formatted += "\n유사한 사례:\n"
        for case in result["similar_cases"]:
            formatted += f"- {case}\n"

    return formatted


def format_policies_result(policies_list: List[Dict[str, Any]]) -> str:
    """
    인스타그램 정책 검색 결과를 포맷팅합니다.

    Args:
        policies_list: 정책 정보 목록

    Returns:
        str: 포맷팅된 결과 문자열
    """
    if not policies_list or "error" in policies_list[0]:
        return f"오류: {policies_list[0].get('error', '알 수 없는 오류')}"

    formatted = "인스타그램 정책 검색 결과:\n\n"

    for i, policy in enumerate(policies_list[:5], 1):
        title = policy.get("title", "제목 없음")
        summary = policy.get("summary", "요약 없음")
        target = policy.get("target", "적용 대상 없음")
        action = policy.get("action", "조치사항 없음")

        formatted += f"{i}. {title}\n"
        formatted += f"   요약: {summary}\n"
        formatted += f"   적용 대상: {target}\n"
        formatted += f"   위반 시 조치: {action}\n\n"

    return formatted


def format_risks_result(risks_list: List[Dict[str, Any]]) -> str:
    """
    컨텐츠 위험 요소 분석 결과를 포맷팅합니다.

    Args:
        risks_list: 위험 요소 분석 결과 목록

    Returns:
        str: 포맷팅된 결과 문자열
    """
    if not risks_list or "error" in risks_list[0]:
        return f"오류: {risks_list[0].get('error', '알 수 없는 오류')}"

    formatted = "컨텐츠 위험 요소 분석 결과:\n\n"

    for i, risk in enumerate(risks_list[:5], 1):
        risk_factors = risk.get("risk_factors", [])
        similar_violations = risk.get("similar_violations", [])
        risk_score = risk.get("risk_score", "N/A")
        recommendations = risk.get("recommendations", [])

        formatted += f"{i}. 위험 요소:\n"
        for factor in risk_factors:
            formatted += f"   - {factor}\n"

        if similar_violations:
            formatted += f"   유사한 위반 사례:\n"
            for violation in similar_violations:
                formatted += f"   - {violation}\n"

        formatted += f"   위험 점수: {risk_score}\n"

        if recommendations:
            formatted += f"   권장사항:\n"
            for rec in recommendations:
                formatted += f"   - {rec}\n"

        formatted += "\n"

    return formatted


def extract_content_from_query(query: str) -> Dict[str, str]:
    """
    쿼리에서 컨텐츠 정보를 추출합니다.

    Args:
        query: 사용자 쿼리

    Returns:
        Dict[str, str]: 추출된 컨텐츠 정보
    """
    # 간단한 키워드 기반 추출 (실제로는 더 정교한 NLP가 필요)
    content_type = "text"

    if any(keyword in query.lower() for keyword in ["이미지", "image", "사진"]):
        content_type = "image"
    elif any(keyword in query.lower() for keyword in ["비디오", "video", "영상"]):
        content_type = "video"
    elif any(keyword in query.lower() for keyword in ["스토리", "story"]):
        content_type = "story"
    elif any(keyword in query.lower() for keyword in ["릴", "reel"]):
        content_type = "reel"

    return {"content_text": query, "content_type": content_type}


def extract_policy_keywords_from_query(query: str) -> str:
    """
    쿼리에서 정책 검색 키워드를 추출합니다.

    Args:
        query: 사용자 쿼리

    Returns:
        str: 추출된 정책 키워드
    """
    # 간단한 키워드 추출 (실제로는 더 정교한 NLP가 필요)
    # 정책, 가이드라인 등의 키워드를 제거하고 핵심 키워드만 추출
    remove_words = [
        "정책",
        "policy",
        "가이드라인",
        "guideline",
        "검색",
        "search",
        "찾아",
        "분석",
    ]

    keywords = query
    for word in remove_words:
        keywords = keywords.replace(word, "").strip()

    return keywords if keywords else "Instagram community guidelines"
