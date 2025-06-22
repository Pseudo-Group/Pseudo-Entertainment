# Management Workflow 로컬 실행 가이드

웹 UI 없이 management 워크플로우를 로컬에서 직접 실행하는 방법입니다.

## 준비사항

1. `.env` 파일에 필요한 API 키가 설정되어 있어야 합니다:
   ```
   OPENAI_API_KEY=sk-...
   TAVILY_API_KEY=tvly-...  # 선택사항 (없으면 모의 검색 사용)
   ```

2. 가상환경이 활성화되어 있어야 합니다:
   ```bash
   uv venv
   uv sync --package management
   ```

## 실행 방법

### 방법 1: Jupyter Notebook 사용 (추천)

```bash
# Jupyter 실행
uv run jupyter notebook test_management_workflow.ipynb
```

노트북에서 셀을 순서대로 실행하면서 각 단계를 확인할 수 있습니다.

### 방법 2: Python 스크립트 실행

#### 간단한 테스트:
```bash
uv run python run_management_quick.py
```

#### 전체 테스트:
```bash
uv run python test_management_simple.py
```

### 방법 3: Python 인터프리터에서 직접 실행

```python
# Python 인터프리터 실행
uv run python

# 다음 코드 입력
from agents.management.workflow import ManagementWorkflow

workflow = ManagementWorkflow()
compiled = workflow.build()

result = compiled.invoke({
    "project_id": "TEST-001",
    "request_type": "resource_allocation",
    "query": "콘서트 기획",
    "response": [],
    "team_members": ["기획팀"],
    "resources_available": {"budget": "10억원"}
})

print(result['response'])
```

## 문제 해결

### TAVILY_API_KEY 오류가 발생하는 경우

1. `.env` 파일에 `TAVILY_API_KEY`가 없거나 잘못된 경우 모의 검색 도구가 사용됩니다.
2. 실제 웹 검색을 원한다면 [Tavily](https://tavily.com)에서 API 키를 발급받아 `.env`에 추가하세요.

### ModuleNotFoundError가 발생하는 경우

```bash
# 프로젝트 루트 디렉토리에서 실행하고 있는지 확인
cd C:\cursor\Act1-Entertainment

# 필요한 패키지 재설치
uv sync --package management
```

### OpenAI API 오류가 발생하는 경우

1. `.env` 파일의 `OPENAI_API_KEY`가 유효한지 확인
2. API 키에 충분한 크레딧이 있는지 확인

## 커스터마이징

`test_management_workflow.ipynb` 또는 `test_management_simple.py`를 수정하여 다양한 시나리오를 테스트할 수 있습니다:

- 프로젝트 ID 변경
- 요청 유형 변경 (resource_allocation, team_management, creator_development)
- 쿼리 내용 수정
- 팀 구성원 및 가용 리소스 조정
