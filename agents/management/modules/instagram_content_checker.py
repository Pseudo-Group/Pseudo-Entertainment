"""
인스타그램 컨텐츠 검수 모듈

이 모듈은 Perplexity MCP를 연동하여 인스타그램에 업로드할 컨텐츠가
적절한지 검수하는 기능을 제공합니다.
"""

import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class ContentType(Enum):
    """컨텐츠 유형"""
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"
    STORY = "story"
    REEL = "reel"


class ContentCategory(Enum):
    """컨텐츠 카테고리"""
    ENTERTAINMENT = "entertainment"
    NEWS = "news"
    LIFESTYLE = "lifestyle"
    TECHNOLOGY = "technology"
    EDUCATION = "education"
    OTHER = "other"


@dataclass
class ContentCheckResult:
    """컨텐츠 검수 결과"""
    is_approved: bool
    score: float  # 0.0 ~ 1.0
    reasons: List[str]
    warnings: List[str]
    suggestions: List[str]
    risk_level: str  # "low", "medium", "high"
    category: ContentCategory
    tags: List[str]


class InstagramContentChecker:
    """인스타그램 컨텐츠 검수기"""
    
    def __init__(self, perplexity_api_key: Optional[str] = None, openai_api_key: Optional[str] = None):
        """
        초기화
        
        Args:
            perplexity_api_key: Perplexity API 키
            openai_api_key: OpenAI API 키 (백업용)
        """
        self.perplexity_api_key = perplexity_api_key or os.getenv("PERPLEXITY_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if self.openai_api_key:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                api_key=self.openai_api_key
            )
        else:
            self.llm = None
    
    async def check_content(
        self,
        content_text: str,
        content_type: ContentType = ContentType.TEXT,
        category: Optional[ContentCategory] = None,
        target_audience: Optional[str] = None,
        brand_guidelines: Optional[str] = None
    ) -> ContentCheckResult:
        """
        컨텐츠 검수 수행
        
        Args:
            content_text: 검수할 컨텐츠 텍스트
            content_type: 컨텐츠 유형
            category: 컨텐츠 카테고리
            target_audience: 타겟 오디언스
            brand_guidelines: 브랜드 가이드라인
            
        Returns:
            ContentCheckResult: 검수 결과
        """
        # Perplexity MCP를 통한 검수 시도
        if self.perplexity_api_key:
            try:
                return await self._check_with_perplexity(
                    content_text, content_type, category, target_audience, brand_guidelines
                )
            except Exception as e:
                print(f"Perplexity 검수 실패: {e}")
        
        # OpenAI를 통한 백업 검수
        if self.llm:
            return await self._check_with_openai(
                content_text, content_type, category, target_audience, brand_guidelines
            )
        
        raise ValueError("API 키가 설정되지 않았습니다.")
    
    async def _check_with_perplexity(
        self,
        content_text: str,
        content_type: ContentType,
        category: Optional[ContentCategory],
        target_audience: Optional[str],
        brand_guidelines: Optional[str]
    ) -> ContentCheckResult:
        """Perplexity MCP를 통한 검수"""
        
        # 검수 프롬프트 구성
        prompt = self._build_check_prompt(
            content_text, content_type, category, target_audience, brand_guidelines
        )
        
        # Perplexity API 호출
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.perplexity_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": [
                        {
                            "role": "system",
                            "content": "당신은 인스타그램 컨텐츠 검수 전문가입니다. 주어진 컨텐츠가 인스타그램에 적합한지 분석하고 JSON 형태로 결과를 반환합니다."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.1
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Perplexity API 오류: {response.status_code}")
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # JSON 파싱
            try:
                parsed_result = json.loads(content)
                return self._parse_check_result(parsed_result)
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 텍스트 분석
                return self._fallback_parse(content)
    
    async def _check_with_openai(
        self,
        content_text: str,
        content_type: ContentType,
        category: Optional[ContentCategory],
        target_audience: Optional[str],
        brand_guidelines: Optional[str]
    ) -> ContentCheckResult:
        """OpenAI를 통한 백업 검수"""
        
        prompt = self._build_check_prompt(
            content_text, content_type, category, target_audience, brand_guidelines
        )
        
        messages = [
            SystemMessage(content="당신은 인스타그램 컨텐츠 검수 전문가입니다. 주어진 컨텐츠가 인스타그램에 적합한지 분석하고 JSON 형태로 결과를 반환합니다."),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        content = response.content
        
        try:
            parsed_result = json.loads(content)
            return self._parse_check_result(parsed_result)
        except json.JSONDecodeError:
            return self._fallback_parse(content)
    
    def _build_check_prompt(
        self,
        content_text: str,
        content_type: ContentType,
        category: Optional[ContentCategory],
        target_audience: Optional[str],
        brand_guidelines: Optional[str]
    ) -> str:
        """검수 프롬프트 구성"""
        
        prompt = f"""
다음 인스타그램 컨텐츠를 검수해주세요:

**컨텐츠 유형**: {content_type.value}
**컨텐츠 텍스트**: {content_text}

"""
        
        if category:
            prompt += f"**카테고리**: {category.value}\n"
        
        if target_audience:
            prompt += f"**타겟 오디언스**: {target_audience}\n"
        
        if brand_guidelines:
            prompt += f"**브랜드 가이드라인**: {brand_guidelines}\n"
        
        prompt += """
다음 기준으로 검수해주세요:
1. 인스타그램 커뮤니티 가이드라인 준수 여부
2. 적절성 및 품질
3. 타겟 오디언스 적합성
4. 브랜드 가이드라인 준수 여부
5. 잠재적 위험 요소

다음 JSON 형태로 결과를 반환해주세요:
{
    "is_approved": true/false,
    "score": 0.0-1.0,
    "reasons": ["승인/거부 이유들"],
    "warnings": ["경고사항들"],
    "suggestions": ["개선 제안사항들"],
    "risk_level": "low/medium/high",
    "category": "카테고리명",
    "tags": ["관련 태그들"]
}
"""
        
        return prompt
    
    def _parse_check_result(self, result: Dict[str, Any]) -> ContentCheckResult:
        """검수 결과 파싱"""
        
        return ContentCheckResult(
            is_approved=result.get("is_approved", False),
            score=float(result.get("score", 0.0)),
            reasons=result.get("reasons", []),
            warnings=result.get("warnings", []),
            suggestions=result.get("suggestions", []),
            risk_level=result.get("risk_level", "medium"),
            category=ContentCategory(result.get("category", "other")),
            tags=result.get("tags", [])
        )
    
    def _fallback_parse(self, content: str) -> ContentCheckResult:
        """텍스트 기반 폴백 파싱"""
        
        # 간단한 키워드 기반 분석
        content_lower = content.lower()
        
        # 위험 키워드 체크
        risk_keywords = ["폭력", "성적", "혐오", "차별", "불법", "스팸"]
        high_risk_keywords = ["폭력", "성적", "혐오"]
        
        risk_level = "low"
        if any(keyword in content_lower for keyword in high_risk_keywords):
            risk_level = "high"
        elif any(keyword in content_lower for keyword in risk_keywords):
            risk_level = "medium"
        
        is_approved = risk_level == "low"
        score = 0.8 if is_approved else 0.3
        
        return ContentCheckResult(
            is_approved=is_approved,
            score=score,
            reasons=["자동 분석 결과"],
            warnings=[],
            suggestions=["수동 검토 권장"],
            risk_level=risk_level,
            category=ContentCategory.OTHER,
            tags=[]
        )


class ContentCheckRequest(BaseModel):
    """컨텐츠 검수 요청 모델"""
    content_text: str = Field(..., description="검수할 컨텐츠 텍스트")
    content_type: ContentType = Field(default=ContentType.TEXT, description="컨텐츠 유형")
    category: Optional[ContentCategory] = Field(default=None, description="컨텐츠 카테고리")
    target_audience: Optional[str] = Field(default=None, description="타겟 오디언스")
    brand_guidelines: Optional[str] = Field(default=None, description="브랜드 가이드라인")


class ContentCheckResponse(BaseModel):
    """컨텐츠 검수 응답 모델"""
    is_approved: bool = Field(..., description="승인 여부")
    score: float = Field(..., description="적합성 점수 (0.0-1.0)")
    reasons: List[str] = Field(..., description="승인/거부 이유")
    warnings: List[str] = Field(default_factory=list, description="경고사항")
    suggestions: List[str] = Field(default_factory=list, description="개선 제안")
    risk_level: str = Field(..., description="위험도 (low/medium/high)")
    category: str = Field(..., description="카테고리")
    tags: List[str] = Field(default_factory=list, description="관련 태그") 