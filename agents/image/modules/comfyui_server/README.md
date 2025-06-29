# 의존성 설치 방법

- 만약 MACOS 가 아니어서 오류가 나서 새로 의존성을 설치해야한다면
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

## Server Test 방법

### 1. ComfyUI 의 main.py 실행

```bash
uv run main.py
```

### 2. comfyui-mcp-server 내의 server.py 실행

```bash
uv run server.py
```

### 3. comfyui-mcp-server 내의 client.py 실행

```bash
uv run client.py
```

- ComfyUI/input 내의 `try_01.png` 파일을 이용하여 얼굴 생성 시작

# 모델 weight 가져오기

- file 경로 : `ComfyUI/models`

```bash
https://huggingface.co/nonsignal007/hyperlora_models/resolve/main/models.zip
```