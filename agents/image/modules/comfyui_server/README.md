# 의존성 설치 방법

- 만약 MACOS 가 아니어서 오류가 나서 새로 의존성을 성치해야한다면
- python version 은 3.12 여야한다.

## 1. uv init, uv venv
```bash
uv init
uv venv
```

## 2. uv add -r requirements.txt

```bash
find . -name "requirements.txt" -exec uv add -r {} \;
```
