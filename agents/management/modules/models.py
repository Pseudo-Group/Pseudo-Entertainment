"""모델 설정 함수 모듈

기본적으로 사용할 모델 인스턴스를 설정하고 생성하고 반환시킵니다.
또한 02_data_model.md에 정의된 데이터 모델들과 03_API_specification.md의 에러 클래스들을 포함합니다.
"""

from dataclasses import dataclass
from typing import Optional
from langchain_openai import ChatOpenAI


def get_openai_model(temperature=0.7, top_p=0.9, response_format=None):
    """
    LangChain에서 사용할 OpenAI 모델을 초기화하여 반환합니다.

    환경변수에서 OPENAI_API_KEY를 가져와 사용하기 때문에, .env 파일에 유효한 API 키가 설정되어 있어야 합니다.
    
    Args:
        temperature: 창의성 조절 (0.0-1.0)
        top_p: 다양성 조절 (0.0-1.0)
        response_format: JSON 출력 강제 시 {"type": "json_object"} 사용

    Returns:
        ChatOpenAI: 초기화된 OpenAI 모델 인스턴스
    """
    # OpenAI 모델 초기화 및 반환
    kwargs = {
        "model": "gpt-4o-mini", 
        "temperature": temperature, 
        "top_p": top_p,
        "max_tokens": 2000
    }
    
    # JSON 형식 응답이 필요한 경우
    if response_format:
        kwargs["response_format"] = response_format
    
    return ChatOpenAI(**kwargs)


# ============================================================================
# 03_API_specification.md 섹션 3.1: 에러 타입 정의
# ============================================================================

class ManagementAPIError(Exception):
    """기본 API 에러"""
    pass


class TavilySearchError(ManagementAPIError):
    """Tavily 검색 에러"""
    pass


class KeywordExtractionError(ManagementAPIError):
    """키워드 추출 에러"""
    pass


class IssueAnalysisError(ManagementAPIError):
    """이슈 분석 에러"""
    pass


class LLMResponseError(ManagementAPIError):
    """LLM 응답 파싱 에러"""
    pass


# ============================================================================
# 02_data_model.md: 데이터 모델 정의
# ============================================================================

@dataclass
class SearchResult:
    """
    검색 결과를 나타내는 데이터 클래스
    02_data_model.md 섹션 2.1에 정의된 구조
    """
    # 기본 정보
    title: str                          # 기사 제목
    content: str                        # 기사 내용 요약
    url: str                           # 기사 URL
    
    # 메타데이터
    published_date: str                # 발행일 (ISO 8601)
    source: str                        # 출처 (언론사명)
    
    # 품질 지표
    relevance_score: float             # 관련성 점수 (0.0-1.0)
    snippet: str                       # 검색 결과 스니펫
    
    # 03_API_specification.md 추가 필드
    raw_content: Optional[str] = None  # Tavily include_raw_content=True 시 사용


@dataclass
class IssueAnalysis:
    """
    이슈 분석 결과를 나타내는 데이터 클래스
    02_data_model.md 섹션 2.2에 정의된 구조
    """
    # 원본 데이터
    original_result: SearchResult       # 분석 대상 검색 결과
    
    # 이슈 분석 결과
    is_issue: bool                     # 이슈 여부 (True/False)
    severity_level: int                # 심각도 등급 (1-4)
    issue_category: str                # 이슈 카테고리
    
    # 분석 내용
    summary: str                       # 이슈 요약 (최대 200자)
    potential_impact: str              # 예상 파급효과 (최대 300자)
    
    # 품질 지표
    confidence_score: float            # 분석 신뢰도 (0.0-1.0)
    analysis_reasoning: str            # 분석 근거 (최대 400자)


# 심각도 등급 정의
SEVERITY_LEVELS = {
    1: "낮음 - 경미한 비판, 개인 의견 차이",
    2: "보통 - 일부 부정적 반응, 논란의 여지",
    3: "높음 - 광범위한 비판, 사과 필요 수준",
    4: "심각 - 사회적 파장, 활동 중단 고려 수준"
}

# 이슈 카테고리 정의
ISSUE_CATEGORIES = {
    "발언": "부적절한 발언, 정치적/사회적 발언",
    "행동": "공적 장소 행동, 팬 서비스 관련",
    "컨텐츠": "작품 내용, 광고, 협업 관련",
    "개인": "사생활, 인간관계 관련"
}
