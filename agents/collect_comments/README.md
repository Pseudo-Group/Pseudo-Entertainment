# 댓글 수집 모듈 (Comment Collection Module)

## 개요

이 모듈은 **ProAct0 Entertainment**의 인스타그램 콘텐츠 댓글 수집을 담당하는 LangGraph Workflow입니다.  
지정한 인스타그램 계정의 게시물에서 댓글을 수집하고, 이를 CSV로 저장하는 작업을 수행합니다.

## 주요 노드

- **InitDriverNode**: 크롬 드라이버 초기화
- **CollectPostLinksNode**: 게시물 링크 수집  
  → **수집할 링크 수는 설정에 따라 지정 가능**
- **SetCurrentPostUrlNode**: 현재 게시물 URL 설정
- **LoadCommentsNode**: 게시물 페이지 로드
- **ExtractCommentsNode**: 댓글 추출
- **SaveCommentsNode**: 댓글 CSV 저장

## 구조


```
comment_collection/
├── modules/ # 모듈 구성 요소
│ ├── chains.py # LangChain 체인 정의 (필요 시)
│ ├── conditions.py # 조건부 라우팅 함수
│ ├── models.py # 사용하는 LLM 모델 설정 (선택)
│ ├── nodes.py # Workflow 노드 클래스 정의
│ ├── persona.py # 페르소나 관리 기능 (선택)
│ ├── prompts.py # 프롬프트 템플릿 (선택)
│ ├── state.py # 상태 정의
│ ├── tools.py # 도구 함수
│ └── utils.py # 유틸리티 함수
├── pyproject.toml # 프로젝트 관리자
├── README.md # 이 문서
└── workflow.py # 댓글 수집 Workflow 정의
```


## 사용 방법

댓글 수집 Workflow는 다음과 같이 사용할 수 있습니다:

```python
from agents.comment_collection.workflow import collect_comments_workflow
from agents.comment_collection.modules.state import CollectCommentsState

# 초기 상태 설정
initial_state = CollectCommentsState(
    profile_url="https://instagram.com/rozy.gram/"
)

# Workflow 실행
compiled = collect_comments_workflow()

# invoke() 사용해 recursion limit 조정하여 수집 가능 범위 확장
result = compiled.invoke(
    CollectCommentsState(profile_url="https://instagram.com/rozy.gram/"),
    config={"recursion_limit": 50}
)

```

## 확장 방법

이 모듈은 확장성을 고려하여 설계되었습니다. 새로운 기능(백로그)을 추가하려면:

1. `modules/nodes.py`에 새로운 노드 클래스 추가
2. 필요에 따라 `modules/state.py`에 상태 관리 추가
3. 필요에 따라 `model.py`, `chain.py` 등의 해당 노드에서 사용되는 관련 모듈을 수정/추가하세요.
4. `workflow.py`에서 Workflow에 새 노드를 엣지로 연결

## 라이센스

이 모듈은 ProAct0 Entertainment의 내부 프로젝트로, 회사 정책에 따른 라이센스가 적용됩니다.