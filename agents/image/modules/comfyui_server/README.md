# 의존성 설치 방법

- 만약 MACOS 가 아니어서 오류가 나서 새로 의존성을 설치해야한다면
- python version 은 3.12 여야한다.

## 1. uv sync
```bash
uv sync
```

## Server Test 방법

### 1. ComfyUI 의 main.py 실행

```bash
uv run ComfyUI/main.py
```

### 2. comfyui-mcp-server 내의 server.py 실행

```bash
uv run comfyui-mcp-server/server.py
```

# 모델 weight 가져오기

- file 경로 : `ComfyUI/models`

```bash
https://huggingface.co/nonsignal007/hyperlora_models/resolve/main/models.zip
```