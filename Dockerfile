FROM python:3.11-slim

WORKDIR /app

# Poetry 설치
RUN pip install poetry

# 프로젝트 파일 복사
COPY pyproject.toml poetry.lock ./

# 의존성 설치
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# 소스 코드 복사
COPY . .

# langgraph.json 파일 생성
RUN echo '{"version": "0.1.0", "name": "pseudo-entertainment-company"}' > langgraph.json

# LangGraph Studio 실행
CMD ["poetry", "run", "langgraph", "studio"] 