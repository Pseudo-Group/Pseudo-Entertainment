# 관리 모듈 (Management Module)

## 개요

이 모듈은 Act 1: Entertainment의 콘텐츠 관리를 담당하는 LangGraph Workflow입니다. 프로젝트, 팀, 리소스의 관리와 크리에이터 직업 성장을 지원하기 위한 주요 노드와 Workflow를 제공합니다.

## 주요 노드

<!-- 노드에 대한 설명을 추가해주세요. -->

## 구조

```
management/
├── modules/            # 모듈 구성 요소
│   ├── chains.py      # LangChain 체인 정의
│   ├── conditions.py  # 조건부 라우팅 함수
│   ├── models.py      # 사용하는 LLM 모델 설정
│   ├── nodes.py       # Workflow 노드 클래스들 정의
│   ├── persona.py     # 페르소나 관리 기능
│   ├── prompts.py     # 프롬프트 템플릿
│   ├── state.py       # 상태 정의
│   ├── tools.py       # 도구 함수
│   └── utils.py       # 유틸리티 함수
├── pyproject.toml     # 프로젝트 관리자
├── README.md          # 이 문서
└── workflow.py        # Management Agent의 Workflow들 정의
```

## 사용 방법

관리(Management) Workflow는 다음과 같이 사용할 수 있습니다:

```python
from agents.management.workflow import management_workflow

# 초기 상태 설정
initial_state = {
    "project_id": "PRJ-2023-001",      # 프로젝트 ID
    "request_type": "resource_allocation",  # 요청 유형
    "query": "개발 팀 리소스 계획 수립",   # 사용자 쿼리
    "team_members": ["Kim", "Lee", "Park"], # 팀 구성원
    "response": []                      # 응답 메시지 (빈 리스트로 초기화)
}

# Workflow 실행
result = management_workflow().invoke(initial_state)
```

## 확장 방법

이 모듈은 확장성을 고려하여 설계되었습니다. 새로운 기능(백로그)을 추가하려면:

1. `modules/nodes.py`에 새로운 노드 클래스 추가
2. 필요에 따라 `modules/state.py`에 상태 관리 추가
3. 필요에 따라 `model.py`, `chain.py` 등의 해당 노드에서 사용되는 관련 모듈을 수정/추가하세요.
4. `workflow.py`에서 Workflow에 새 노드를 엣지로 연결

## 라이센스

이 모듈은 Proact0의 Act 1: Entertainment의 내부 프로젝트로, 그룹 정책에 따른 라이센스가 적용됩니다.