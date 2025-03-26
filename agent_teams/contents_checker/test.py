import os
import requests

from typing import Dict
from dotenv import load_dotenv

from PIL import Image
from langgraph.graph import StateGraph

def check_image_validity(image_path) -> bool:
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def check_text_instagram_format(text) -> bool:
    return len(text) <= 2200

def check_sensitive_text(text) -> bool:
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-guard-3-8b",
        "messages": [{"role": "user", "content": text}]
    }
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        return "safe" in result.get("choices", [{}])[0].get("message", {}).get("content", "")
    return False

def validate_content(content: Dict) -> str:
    # 이미지가 없는 경우 (인스타에는 이미지 없이 업로드 불가능, 텍스트는 없어도 됨)
    if 'image' not in content or not content['image']:
        return "missing_image"

    # 유효하지 않은 이미지인 경우
    if not check_image_validity(content['image']):
        return "invalid image"

    # 텍스트 길이가 2200자를 넘는 경우
    if not check_text_instagram_format(content['text']):
        return "invalid text"

    # 안전하지 않은 text인 경우
    if not check_sensitive_text(content['text']):
        return "unsafe text"

    return "valid"

def content_checker_flow(content: Dict) -> Dict:
    result = validate_content(content)
    return {"status": result, "content": content}

def build_graph():
    graph = StateGraph(input=Dict, output=Dict)

    graph.add_node("check_content", content_checker_flow)

    graph.set_entry_point("check_content")

    compiled_graph = graph.compile()

    return compiled_graph

if __name__ == '__main__':
    load_dotenv()

    compiled_graph = build_graph()

    test_content = {
        "image": "test_image.jpg",  # 테스트 이미지 경로
        "text": "이것은 인스타그램 포스트에 올릴 테스트 문장입니다.",
        "persona": "casual"
    }

    result = compiled_graph.invoke(test_content)

    print("검사 결과:", result)