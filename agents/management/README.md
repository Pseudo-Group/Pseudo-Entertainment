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

<<<<<<< HEAD
이 모듈은 Pseudo Group의 Pseudo Entertainment Company의 내부 프로젝트로, 그룹 정책에 따른 라이센스가 적용됩니다.

# 인스타그램 API 워크플로우

이 워크플로우는 인스타그램 API를 사용하여 포스트의 댓글 수 변화를 모니터링하는 LangGraph 기반 시스템입니다.

## 기능

- 인스타그램 사용자의 모든 포스트 정보 가져오기
- 첫 번째 포스트의 댓글 수 모니터링
- 댓글 수 변경 시 댓글 데이터 자동 수집
- JSON 파일을 통한 상태 관리

## 워크플로우 구조

```
시작 → 미디어 정보 가져오기 → 댓글 수 확인 → [조건부 분기]
                                                    ↓
                                            댓글 수 변경? → 댓글 데이터 가져오기 → 종료
                                                    ↓
                                            변경 없음 → 종료
```

## 노드 설명

### 1. InstagramMediaFetchNode
- 인스타그램 API를 통해 사용자의 모든 미디어 정보를 가져옵니다
- 첫 번째 미디어 ID를 저장합니다
- JSON 파일에 초기 데이터를 저장합니다

### 2. InstagramCommentsCheckNode
- JSON 파일에서 이전 댓글 수를 읽어옵니다
- 현재 댓글 수와 비교하여 변경 여부를 확인합니다
- 변경이 있으면 `has_changes`를 `True`로 설정합니다

### 3. InstagramCommentsFetchNode
- 댓글 수 변경이 감지되면 실행됩니다
- 첫 번째 미디어의 모든 댓글 데이터를 가져옵니다
- JSON 파일의 댓글 수를 업데이트합니다

### 4. NoChangeNode
- 댓글 수 변경이 없을 때 실행됩니다
- 모니터링을 계속한다는 메시지를 반환합니다

## 사용법

### 1. 환경 설정

```python
# test_instagram_workflow.py 파일에서 실제 인증 정보로 교체
access_token = "YOUR_ACCESS_TOKEN_HERE"  # 실제 액세스 토큰
user_id = "YOUR_USER_ID_HERE"  # 실제 사용자 ID
```

### 2. 워크플로우 실행

```python
from agents.management.workflow import management_workflow
from agents.management.modules.state import ManagementState

# 초기 상태 설정
initial_state = {
    "access_token": "YOUR_ACCESS_TOKEN",
    "user_id": "YOUR_USER_ID",
    "json_file_path": "instagram_data.json",
    "response": []
}

# 워크플로우 실행
workflow = management_workflow.build()
result = workflow.invoke(initial_state)
```

### 3. 테스트 실행

```bash
python agents/management/test_instagram_workflow.py
```

## JSON 파일 구조

워크플로우 실행 시 생성되는 `instagram_data.json` 파일의 구조:

```json
{
  "media_data": [
    {
      "id": "18007485335525524",
      "caption": "정호영 쉐프의 냉제육...",
      "media_type": "IMAGE",
      "timestamp": "2024-05-18T17:56:11+0000",
      "username": "yimbapchunguk",
      "like_count": 13,
      "comments_count": 6
    }
  ],
  "first_media_id": "18007485335525524",
  "previous_comments_count": 6
}
```

## 상태 필드

- `access_token`: 인스타그램 액세스 토큰
- `user_id`: 인스타그램 사용자 ID
- `json_file_path`: JSON 파일 경로
- `media_data`: 미디어 데이터 목록
- `first_media_id`: 첫 번째 미디어 ID
- `current_comments_count`: 현재 댓글 수
- `previous_comments_count`: 이전 댓글 수
- `comments_data`: 댓글 데이터
- `has_changes`: 댓글 수 변경 여부
- `response`: 응답 메시지 목록

## 주의사항

1. **API 인증**: 유효한 인스타그램 액세스 토큰이 필요합니다
2. **API 제한**: Instagram API의 요청 제한을 고려해야 합니다
3. **토큰 갱신**: 액세스 토큰은 60일 후 만료되므로 주기적으로 갱신해야 합니다
4. **파일 권한**: JSON 파일 생성 및 수정 권한이 필요합니다

## 에러 처리

워크플로우는 다음과 같은 에러 상황을 처리합니다:

- API 요청 실패
- JSON 파일 읽기/쓰기 오류
- 미디어 ID 누락
- 네트워크 연결 오류

각 노드에서 발생하는 오류는 적절한 에러 메시지와 함께 처리됩니다.
=======
이 모듈은 Proact0의 Act 1: Entertainment의 내부 프로젝트로, 그룹 정책에 따른 라이센스가 적용됩니다.
>>>>>>> b1d55b8490d69551c6e56e00b36ca68e030e7abc
