import json
import os
from typing import Any, Dict, List

import httpx
from mcp.server.fastmcp import FastMCP

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
MCP_CONTENTS_HOST = os.getenv("MCP_CONTENTS_HOST", "0.0.0.0")
MCP_CONTENTS_PORT = int(os.getenv("MCP_CONTENTS_PORT", 8200))
MCP_CONTENTS_TRANSPORT = os.getenv("MCP_CONTENTS_TRANSPORT", "stdio")

contents_mcp = FastMCP(
    name="contents_verify",
    instructions=(
        "Act as an Instagram content verification assistant that checks if content "
        "is appropriate for Instagram posting using real-time web search."
    ),
    host=MCP_CONTENTS_HOST,
    port=MCP_CONTENTS_PORT,
)


@contents_mcp.tool()
async def verify_instagram_content(
    content_text: str, content_type: str = "text"
) -> Dict[str, Any]:
    """
    Perplexity API를 사용하여 인스타그램 컨텐츠의 적절성을 실시간 웹 검색으로 검증합니다.

    Args:
        content_text (str): 검증할 컨텐츠 텍스트
        content_type (str): 컨텐츠 유형 (text, image, video, story, reel)

    Returns:
        Dict[str, Any]: 검증 결과
    """
    if not PERPLEXITY_API_KEY:
        return {
            "error": "PERPLEXITY_API_KEY가 설정되지 않았습니다.",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["API 키가 없어 검증을 수행할 수 없습니다."],
            "warnings": [],
            "suggestions": ["PERPLEXITY_API_KEY를 설정해주세요."],
            "risk_level": "high",
            "content_type": content_type,
            "tags": [],
        }

    try:
        # Perplexity API를 통한 인스타그램 정책 검색 및 컨텐츠 검증
        prompt = f"""
다음 인스타그램 컨텐츠를 검증해주세요:

컨텐츠 유형: {content_type}
컨텐츠 텍스트: {content_text}

실시간 웹 검색을 통해 다음을 확인해주세요:
1. 인스타그램 커뮤니티 가이드라인 및 정책
2. 유사한 컨텐츠의 위반 사례
3. 현재 인스타그램에서 금지하는 키워드나 주제
4. 최근 인스타그램 정책 변경사항
5. 해당 컨텐츠의 잠재적 위험 요소

검색 키워드 예시:
- "Instagram community guidelines 2024"
- "Instagram content policy violations"
- "Instagram banned content examples"
- "Instagram content moderation rules"

다음 JSON 형태로 결과를 반환해주세요:
{{
    "is_approved": true/false,
    "score": 0.0-1.0,
    "reasons": ["승인/거부 이유들 (웹 검색 결과 기반)"],
    "warnings": ["경고사항들"],
    "suggestions": ["개선 제안사항들"],
    "risk_level": "low/medium/high",
    "policy_references": ["참조한 정책들"],
    "similar_cases": ["유사한 사례들"],
    "tags": ["관련 태그들"]
}}
"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": [
                        {
                            "role": "system",
                            "content": "당신은 인스타그램 컨텐츠 검증 전문가입니다. 실시간 웹 검색을 통해 최신 인스타그램 정책과 위반 사례를 확인하고, 주어진 컨텐츠가 인스타그램에 적합한지 분석합니다.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.1,
                },
            )

            if response.status_code != 200:
                raise Exception(f"Perplexity API 오류: {response.status_code}")

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # JSON 파싱
            try:
                parsed_result = json.loads(content)
                return {
                    "is_approved": parsed_result.get("is_approved", False),
                    "score": float(parsed_result.get("score", 0.0)),
                    "reasons": parsed_result.get("reasons", []),
                    "warnings": parsed_result.get("warnings", []),
                    "suggestions": parsed_result.get("suggestions", []),
                    "risk_level": parsed_result.get("risk_level", "medium"),
                    "content_type": content_type,
                    "policy_references": parsed_result.get("policy_references", []),
                    "similar_cases": parsed_result.get("similar_cases", []),
                    "tags": parsed_result.get("tags", []),
                }
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 폴백 분석
                return _fallback_analysis(content_text, content_type)

    except Exception as e:
        return {
            "error": f"검증 중 오류 발생: {str(e)}",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["검증 중 오류가 발생했습니다."],
            "warnings": [],
            "suggestions": ["다시 시도해주세요."],
            "risk_level": "medium",
            "content_type": content_type,
            "tags": [],
        }


@contents_mcp.tool()
async def search_instagram_policies(keywords: str) -> List[Dict[str, Any]]:
    """
    인스타그램 정책 및 가이드라인을 검색합니다.

    Args:
        keywords (str): 검색할 정책 키워드

    Returns:
        List[Dict[str, Any]]: 정책 정보 목록
    """
    if not PERPLEXITY_API_KEY:
        return [{"error": "PERPLEXITY_API_KEY가 설정되지 않았습니다."}]

    try:
        prompt = f"""
다음 키워드로 인스타그램 정책 및 가이드라인을 검색해주세요: {keywords}

다음 정보를 포함하여 JSON 형태로 반환해주세요:
- 정책 제목
- 정책 내용 요약
- 적용 대상
- 위반 시 조치사항
- 최신 업데이트 날짜
- 관련 링크

검색 키워드 예시:
- "Instagram community guidelines"
- "Instagram content policy"
- "Instagram banned content"
- "Instagram moderation rules"
"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": [
                        {
                            "role": "system",
                            "content": "당신은 인스타그램 정책 전문가입니다. 최신 인스타그램 정책과 가이드라인을 검색하고 구조화된 정보를 제공합니다.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.1,
                },
            )

            if response.status_code != 200:
                raise Exception(f"Perplexity API 오류: {response.status_code}")

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            try:
                parsed_result = json.loads(content)
                return (
                    parsed_result
                    if isinstance(parsed_result, list)
                    else [parsed_result]
                )
            except json.JSONDecodeError:
                return [{"content": content, "error": "JSON 파싱 실패"}]

    except Exception as e:
        return [{"error": f"정책 검색 중 오류 발생: {str(e)}"}]


@contents_mcp.tool()
async def analyze_content_risks(content_text: str) -> List[Dict[str, Any]]:
    """
    컨텐츠의 잠재적 위험 요소를 분석합니다.

    Args:
        content_text (str): 분석할 컨텐츠 텍스트

    Returns:
        List[Dict[str, Any]]: 위험 요소 분석 결과
    """
    if not PERPLEXITY_API_KEY:
        return [{"error": "PERPLEXITY_API_KEY가 설정되지 않았습니다."}]

    try:
        prompt = f"""
다음 컨텐츠의 잠재적 위험 요소를 분석해주세요: {content_text}

실시간 웹 검색을 통해 다음을 확인해주세요:
1. 유사한 컨텐츠의 위반 사례
2. 관련 키워드의 위험도
3. 최근 인스타그램에서 제재받은 유사 컨텐츠
4. 법적/윤리적 문제 가능성
5. 브랜드 안전성 위험 요소

다음 JSON 형태로 결과를 반환해주세요:
{{
    "risk_factors": ["위험 요소들"],
    "similar_violations": ["유사한 위반 사례들"],
    "risk_score": 0.0-1.0,
    "recommendations": ["위험 완화 제안사항들"],
    "legal_considerations": ["법적 고려사항들"]
}}
"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": [
                        {
                            "role": "system",
                            "content": "당신은 컨텐츠 위험 분석 전문가입니다. 실시간 웹 검색을 통해 컨텐츠의 잠재적 위험 요소를 분석합니다.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.1,
                },
            )

            if response.status_code != 200:
                raise Exception(f"Perplexity API 오류: {response.status_code}")

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            try:
                parsed_result = json.loads(content)
                return (
                    parsed_result
                    if isinstance(parsed_result, list)
                    else [parsed_result]
                )
            except json.JSONDecodeError:
                return [{"content": content, "error": "JSON 파싱 실패"}]

    except Exception as e:
        return [{"error": f"위험 분석 중 오류 발생: {str(e)}"}]


def _fallback_analysis(content_text: str, content_type: str) -> Dict[str, Any]:
    """Perplexity API 실패 시 폴백 분석"""
    content_lower = content_text.lower()

    # 위험 키워드 체크
    risk_keywords = ["폭력", "성적", "혐오", "차별", "불법", "스팸", "음란", "폭력적"]
    high_risk_keywords = ["폭력", "성적", "혐오", "음란"]

    risk_level = "low"
    if any(keyword in content_lower for keyword in high_risk_keywords):
        risk_level = "high"
    elif any(keyword in content_lower for keyword in risk_keywords):
        risk_level = "medium"

    is_approved = risk_level == "low"
    score = 0.8 if is_approved else 0.3

    reasons = []
    if is_approved:
        reasons.append("컨텐츠가 인스타그램 가이드라인에 적합합니다.")
    else:
        reasons.append("위험 키워드가 포함되어 있어 검토가 필요합니다.")

    warnings = []
    if risk_level == "medium":
        warnings.append("일부 민감한 내용이 포함되어 있습니다.")
    elif risk_level == "high":
        warnings.append("부적절한 내용이 포함되어 있습니다.")

    suggestions = []
    if not is_approved:
        suggestions.append("컨텐츠를 수정하거나 재검토하세요.")
    else:
        suggestions.append("해시태그를 추가하여 가시성을 높이세요.")

    return {
        "is_approved": is_approved,
        "score": score,
        "reasons": reasons,
        "warnings": warnings,
        "suggestions": suggestions,
        "risk_level": risk_level,
        "content_type": content_type,
        "policy_references": [],
        "similar_cases": [],
        "tags": [],
    }


if __name__ == "__main__":
    print(
        f"contents_verify MCP server is running on "
        f"{MCP_CONTENTS_HOST}:{MCP_CONTENTS_PORT}"
    )
    contents_mcp.run(transport=MCP_CONTENTS_TRANSPORT)
