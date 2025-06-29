"""
도구(Tools) 모듈

이 모듈은 Management Workflow에서 사용할 수 있는 다양한 도구를 정의합니다.
도구는 LLM이 프로젝트 관리, 리소스 할당, 팀 관리 등을 지원하는 함수들입니다.

아래는 엔터테인먼트 프로젝트 관리에 적합한 도구의 예시입니다:
- 프로젝트 일정 관리 도구: 일정 생성, 수정, 추적
- 팀 구성원 할당 도구: 팀원 정보 검색 및 역할 할당
- 리소스 검색 도구: 가용 리소스 출력 및 할당 상태 확인
- 참조 자료 검색 도구: 엔터테인먼트 산업의 프로젝트 관리 사례 검색
- 협업 지원 도구: 팀원간 커뮤니케이션 및 협업 지원
- MCP 서버 도구: 인스타그램 컨텐츠 검증, 정책 검색, 위험 요소 분석
"""

import asyncio
from typing import Any, Dict, List, Optional

from agents.management.modules.mcp.mcp_client import (
    analyze_content_risks,
    search_instagram_policies,
    verify_instagram_content,
)


async def verify_instagram_content_tool(
    content_text: str, content_type: str = "text"
) -> Dict[str, Any]:
    """
    MCP 서버를 통해 인스타그램 컨텐츠를 검증하는 도구

    Args:
        content_text: 검증할 컨텐츠 텍스트
        content_type: 컨텐츠 유형 (text, image, video, story, reel)

    Returns:
        Dict[str, Any]: 검증 결과
    """
    try:
        result = await verify_instagram_content(content_text, content_type)
        return result
    except Exception as e:
        return {
            "error": f"인스타그램 컨텐츠 검증 중 오류 발생: {str(e)}",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["검증 중 오류가 발생했습니다."],
            "warnings": [],
            "suggestions": ["다시 시도해주세요."],
            "risk_level": "medium",
            "content_type": content_type,
            "tags": [],
        }


async def search_instagram_policies_tool(keywords: str) -> List[Dict[str, Any]]:
    """
    MCP 서버를 통해 인스타그램 정책을 검색하는 도구

    Args:
        keywords: 검색할 정책 키워드

    Returns:
        List[Dict[str, Any]]: 정책 정보 목록
    """
    try:
        result = await search_instagram_policies(keywords)
        return result
    except Exception as e:
        return [{"error": f"인스타그램 정책 검색 중 오류 발생: {str(e)}"}]


async def analyze_content_risks_tool(content_text: str) -> List[Dict[str, Any]]:
    """
    MCP 서버를 통해 컨텐츠 위험 요소를 분석하는 도구

    Args:
        content_text: 분석할 컨텐츠 텍스트

    Returns:
        List[Dict[str, Any]]: 위험 요소 분석 결과
    """
    try:
        result = await analyze_content_risks(content_text)
        return result
    except Exception as e:
        return [{"error": f"컨텐츠 위험 분석 중 오류 발생: {str(e)}"}]


def search_available_resources(
    resource_type: str, time_period: Optional[Dict[str, Any]] = None
) -> List[Dict]:
    """
    주어진 리소스 유형과 시간에 따라 사용 가능한 리소스를 검색합니다.

    Args:
        resource_type: 검색할 리소스 유형 (예: 'studio', 'equipment', 'staff')
        time_period: 시간 기간 (예: {'start': '2023-06-01', 'end': '2023-06-30'})

    Returns:
        List[Dict]: 사용 가능한 리소스 목록
    """
    # 실제 구현에서는 데이터베이스를 쿼리하거나 API를 호출하여 사용 가능한 리소스를 가져옴
    return [
        {
            "id": "resource_001",
            "type": resource_type,
            "name": f"Sample {resource_type}",
            "status": "available",
            "location": "Studio A",
            "description": f"Available {resource_type} for the specified time period",
        }
    ]


def get_project_schedule(project_id: str) -> Dict:
    """
    특정 프로젝트의 일정을 가져옵니다.

    Args:
        project_id: 프로젝트 ID

    Returns:
        Dict: 프로젝트 일정 정보
    """
    # 실제 구현에서는 프로젝트 관리 시스템 API를 호출하여 일정을 가져옴
    return {
        "project_id": project_id,
        "schedule": {
            "start_date": "2023-06-01",
            "end_date": "2023-12-31",
            "milestones": [
                {"name": "Planning Phase", "date": "2023-06-15"},
                {"name": "Development Phase", "date": "2023-09-30"},
                {"name": "Testing Phase", "date": "2023-11-30"},
                {"name": "Launch", "date": "2023-12-31"},
            ],
        },
    }
