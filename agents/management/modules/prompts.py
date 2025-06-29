"""
03_API_specification.md 섹션 4 기반 프롬프트 템플릿 모듈

구조화된 JSON 응답을 위한 프롬프트들을 정의합니다.
키워드 추출과 이슈 분석에 특화된 프롬프트를 포함합니다.
"""

from langchain_core.prompts import ChatPromptTemplate


# 03_API_specification.md 섹션 4.1: 키워드 추출 프롬프트
KEYWORD_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """당신은 뉴스 키워드 추출 전문가입니다.
주어진 아이유 관련 뉴스에서 현재 트렌딩되는 키워드를 추출해주세요.

추출 기준:
1. 최소 2회 이상 언급된 키워드
2. 아이유와 직접 관련된 키워드
3. 시간적 관련성이 높은 키워드 (최근 활동, 이슈 등)
4. 일반적인 단어 제외 (그녀, 가수, 연예인 등)

출력 형식: JSON
{{
    "keywords": ["키워드1", "키워드2", ...],
    "reasoning": "추출 근거"
}}

주의사항:
- 반드시 유효한 JSON 형식으로 응답하세요
- keywords 배열에는 문자열만 포함하세요
- 각 키워드는 2-20자 사이여야 합니다
- 중복된 키워드는 제거하세요"""),
    ("human", """다음 아이유 관련 뉴스에서 {target_count}개의 키워드를 추출해주세요:

{search_results_formatted}

위 내용을 분석하여 현재 트렌딩되는 핵심 키워드 {target_count}개를 JSON 형식으로 추출해주세요.""")
])


# 03_API_specification.md 섹션 4.2: 이슈 분석 프롬프트
ISSUE_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """당신은 인플루언서 이슈 분석 전문가입니다.
주어진 기사를 분석하여 아이유에게 부정적 영향을 줄 수 있는 이슈인지 판단해주세요.

분석 기준:
1. 이슈 여부: 사회적 논란이나 비판을 받을 수 있는 내용인가?
2. 심각도: 1(경미) ~ 4(심각) 등급
   - 1: 경미한 비판, 개인 의견 차이
   - 2: 일부 부정적 반응, 논란의 여지
   - 3: 광범위한 비판, 사과 필요 수준
   - 4: 사회적 파장, 활동 중단 고려 수준
3. 카테고리: 발언/행동/컨텐츠/개인 중 선택
   - 발언: 부적절한 발언, 정치적/사회적 발언
   - 행동: 공적 장소 행동, 팬 서비스 관련
   - 컨텐츠: 작품 내용, 광고, 협업 관련
   - 개인: 사생활, 인간관계 관련
4. 파급력: 예상되는 사회적 반응

출력 형식: JSON
{{
    "is_issue": true/false,
    "severity_level": 1-4,
    "issue_category": "발언|행동|컨텐츠|개인",
    "summary": "이슈 요약 (200자 이내)",
    "potential_impact": "예상 파급효과 (300자 이내)",
    "confidence_score": 0.0-1.0,
    "reasoning": "분석 근거 (400자 이내)"
}}

주의사항:
- 반드시 유효한 JSON 형식으로 응답하세요
- is_issue는 boolean 타입이어야 합니다
- severity_level은 1-4 사이의 정수여야 합니다
- issue_category는 지정된 4개 카테고리 중 하나여야 합니다
- confidence_score는 0.0-1.0 사이의 실수여야 합니다
- 객관적이고 균형잡힌 분석을 제공하세요"""),
    ("human", """다음 기사를 분석해주세요:

제목: {title}
내용: {content}
출처: {source}
발행일: {published_date}
URL: {url}
관련성 점수: {relevance_score}

위 기사를 분석하여 아이유에게 미칠 수 있는 이슈 여부를 JSON 형식으로 판단해주세요.""")
])


# 추가 프롬프트 템플릿들

# 종합 분석 보고서 생성용 프롬프트 (향후 확장용)
COMPREHENSIVE_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """당신은 인플루언서 종합 분석 전문가입니다.
수집된 모든 이슈 분석 결과를 종합하여 포괄적인 보고서를 작성해주세요.

보고서 구성:
1. 전체 이슈 요약
2. 심각도별 분석
3. 카테고리별 분석  
4. 시간적 트렌드 분석
5. 대응 권장사항

출력 형식: JSON
{{
    "summary": "전체 이슈 요약",
    "severity_analysis": "심각도별 분석",
    "category_analysis": "카테고리별 분석",
    "trend_analysis": "시간적 트렌드 분석",
    "recommendations": ["권장사항1", "권장사항2", ...]
}}"""),
    ("human", """다음 분석 결과들을 종합하여 보고서를 작성해주세요:

총 분석 건수: {total_analyses}
실제 이슈 건수: {real_issues}
심각도 분포: {severity_distribution}
카테고리 분포: {category_distribution}

상세 이슈 목록:
{detailed_issues}

위 정보를 바탕으로 종합 분석 보고서를 JSON 형식으로 작성해주세요.""")
])


def get_keyword_extraction_prompt():
    """키워드 추출 프롬프트를 반환합니다."""
    return KEYWORD_EXTRACTION_PROMPT


def get_issue_analysis_prompt():
    """이슈 분석 프롬프트를 반환합니다."""
    return ISSUE_ANALYSIS_PROMPT


def get_comprehensive_analysis_prompt():
    """종합 분석 프롬프트를 반환합니다."""
    return COMPREHENSIVE_ANALYSIS_PROMPT


# 프롬프트 검증 함수
def validate_prompt_parameters(prompt_name: str, parameters: dict) -> bool:
    """
    프롬프트 매개변수 유효성 검증
    
    Args:
        prompt_name: 프롬프트 이름
        parameters: 매개변수 딕셔너리
        
    Returns:
        bool: 유효성 여부
    """
    if prompt_name == "keyword_extraction":
        required_params = ["search_results_formatted", "target_count"]
        return all(param in parameters for param in required_params)
    
    elif prompt_name == "issue_analysis":
        required_params = ["title", "content", "source", "published_date", "url", "relevance_score"]
        return all(param in parameters for param in required_params)
    
    elif prompt_name == "comprehensive_analysis":
        required_params = ["total_analyses", "real_issues", "severity_distribution", 
                          "category_distribution", "detailed_issues"]
        return all(param in parameters for param in required_params)
    
    return False


# 프롬프트 사용 예시 함수 (디버깅 및 테스트용)
def get_example_parameters():
    """프롬프트 테스트용 예시 매개변수를 반환합니다."""
    return {
        "keyword_extraction": {
            "search_results_formatted": "[결과 1]\n제목: 아이유 새 앨범 발매\n내용: 아이유가 새로운 정규 앨범을 발매한다고 발표했다...\n출처: 연합뉴스",
            "target_count": 5
        },
        "issue_analysis": {
            "title": "아이유, 새 앨범 발매 발표",
            "content": "가수 아이유가 새로운 정규 앨범을 발매한다고 발표했다. 이번 앨범은...",
            "source": "연합뉴스",
            "published_date": "2024-01-15T10:30:00Z",
            "url": "https://example.com/news/123",
            "relevance_score": 0.95
        },
        "comprehensive_analysis": {
            "total_analyses": 25,
            "real_issues": 3,
            "severity_distribution": {1: 2, 2: 1, 3: 0, 4: 0},
            "category_distribution": {"발언": 1, "컨텐츠": 2},
            "detailed_issues": "1. [발언] 정치적 발언 논란 (심각도: 2)\n2. [컨텐츠] 광고 모델 논란 (심각도: 1)"
        }
    }


# 프롬프트 메타데이터
PROMPT_METADATA = {
    "keyword_extraction": {
        "description": "아이유 관련 뉴스에서 트렌딩 키워드를 추출",
        "input_type": "검색 결과 텍스트",
        "output_type": "JSON (keywords, reasoning)",
        "temperature": 0.3,
        "max_tokens": 1000
    },
    "issue_analysis": {
        "description": "개별 기사의 이슈 여부를 분석",
        "input_type": "개별 SearchResult",
        "output_type": "JSON (is_issue, severity_level, category, etc.)",
        "temperature": 0.1,
        "max_tokens": 1500
    },
    "comprehensive_analysis": {
        "description": "모든 이슈 분석 결과를 종합한 보고서 생성",
        "input_type": "이슈 분석 결과 목록",
        "output_type": "JSON (summary, analysis, recommendations)",
        "temperature": 0.5,
        "max_tokens": 2000
    }
}
