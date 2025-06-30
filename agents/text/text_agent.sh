#!/bin/bash
# 텍스트 모듈 의존성 설치
uv sync --package text

# .env, agents/text/.env 파일에서 환경변수 불러오기 (주석/빈줄/이상한 줄 제외)
set -a
source <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env)
source <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' agents/text/.env)
set +a

# 포트 사용 중인 프로세스 종료 함수 (동의 받기)
kill_port() {
  local PORT=$1
  if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    return
  fi
  local PID
  PID=$(lsof -ti tcp:"$PORT")
  if [ -n "$PID" ]; then
    echo "포트 $PORT를 사용 중인 프로세스(PID: $PID)가 있습니다."
    echo -n "종료하시겠습니까? (y/N): "
    read answer
    case "$answer" in
      [yY]|[yY][eE][sS])
        kill -9 $PID
        echo "프로세스(PID: $PID)를 종료했습니다."
        ;;
      *)
        echo "프로세스 종료를 건너뜁니다."
        ;;
    esac
  fi
}

# MCP로 시작하고 PORT로 끝나는 모든 환경변수의 포트에 대해 프로세스 종료
MCP_PORT_VARS=($(env | grep '^MCP.*PORT=' | cut -d= -f1))
for var in "${MCP_PORT_VARS[@]}"; do
  kill_port "${!var}"
done

# LANGGRAPH_PORT에 해당하는 프로세스 종료
kill_port "$LANGGRAPH_PORT"

# 뉴스 MCP 서버 실행
uv run agents/text/mcp/mcp_news_server.py &

# LangGraph 서버 실행
uv run langgraph dev --port "$LANGGRAPH_PORT" &

wait