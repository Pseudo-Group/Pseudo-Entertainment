# Pseudo Entertainment Company

AI 기반 콘텐츠 생성 및 관리 시스템

## 프로젝트 소개

Pseudo Entertainment Company는 LangGraph와 LangChain을 활용한 AI 기반 콘텐츠 생성 및 관리 시스템입니다. 이 프로젝트는 다양한 형태의 콘텐츠를 자동으로 생성하고 관리할 수 있는 도구를 제공합니다.

### 주요 기능

- AI 기반 콘텐츠 생성
- 페르소나 기반 콘텐츠 최적화
- LangGraph를 활용한 워크플로우 관리

## 설치 방법

### 시스템 요구사항

- Python 3.11 이상
- uv (의존성 관리)
- Flake8, Black, Isort (PEP8 스타일 포맷팅)

### 설치 절차

1. 저장소 클론

```bash
$ git clone https://github.com/Pseudo-Group/Pseudo-Entertainment.git
$ cd pseudo-entertainment-company
```

2. uv 설치 (아직 설치되지 않은 경우)

[🔗 uv 설치 방법 링크](https://docs.astral.sh/uv/getting-started/installation/)

3. 개발 환경 활성화

```bash
$ uv venv .venv
$ source .venv/bin/activate
$ (.venv)  # 가상 환경 활성화 완료
```

5. 프로젝트 의존성 설치(최신화)

```bash
$ uv sync
```

## 사용 방법

1. 개발 환경 활성화 확인(개발 환경 활성화를 한 경우에는 건너뜁니다.)

```bash
$ uv venv .venv
$ source .venv/bin/activate
$ (.venv)  # 가상 환경 활성화 완료
```

2. LangGraph 서버 실행

```bash
$ (.venv) uv sync  # 의존성 설치
$ (.venv) uv run langgraph dev
```

서버가 실행되면 다음 URL에서 접근할 수 있습니다:

- API: http://127.0.0.1:2024
- Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- API 문서: http://127.0.0.1:2024/docs

> 참고: 이 서버는 개발 및 테스트용으로 설계된 인메모리 서버입니다. 프로덕션 환경에서는 LangGraph Cloud를 사용하는 것이 권장됩니다.

**실행 화면**

![](media/LangGraph_Studio_after_invoke.png)

3. 변수에 따른 값 입력 후 실행

- 각 Agent 별 `GraphState`에 정의된 Attribute에 따라 변수를 입력합니다.
- `GraphState`는 `agents/{agent_type}/modules/state.py:GraphState`에서 개별 관리됩니다.

**실행 화면**
![](media/LangGraph_Studio_after_invoke.png)

4. 터미널에서 종료
- window: `ctrl + c`, macOS: `cmd + c`

## 프로젝트 참여 방법

**TODO: 업데이트 필요**

### 💡 **NOTE**:

- 형식 및 가이드에 맞춰서 Commit Message, Issue, Pull Request를 작성해주세요. 상세 설명은 [여기(내부 링크)](https://www.notion.so/hon2ycomb/Git-Commit-Message-Convention-1b000c82b1388185aa3cf88a7e57f24c?pvs=4)를 참조하세요 :)
- 본 프로젝트에서 PR 후 merge하는 경우, github action으로 포맷팅 검사를 진행합니다. vscode 및 cursor에서 포맷팅 세팅은 [여기](https://gamchan.notion.site/vscode-9b61026771cb4121bbb80d4d4f289bc2)를 참조하세요 :)
