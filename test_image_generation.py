from agents.image.modules.nodes import ImageGenerationNode, TextResponseNode

def test_image_and_text_generation():
    # 노드 인스턴스 생성
    image_node = ImageGenerationNode()
    text_node = TextResponseNode()
    
    # 테스트용 입력 데이터
    test_input = {
        "purpose": "앨범커버_테스트",
        "text": "도시의 밤거리, 네온사인이 빛나는 거리에서 비가 내리고 있다. 레트로한 감성의 사이버펑크 스타일."
    }
    
    print("=== 이미지 생성 시작 ===")
    image_result = image_node.execute(test_input)
    
    print("\n이미지 생성 결과:")
    print(f"상태: {image_result['status']}")
    print(f"목적: {image_result['purpose']}")
    print(f"입력 텍스트: {image_result['text']}")
    
    if image_result['status'] == 'success':
        print(f"\n이미지가 다음 경로에 저장되었습니다: {image_result['image_path']}")
    else:
        print(f"\n이미지 생성 에러: {image_result.get('error', '알 수 없는 에러')}")

    print("\n=== 텍스트 응답 생성 시작 ===")
    text_result = text_node.execute(test_input)
    
    print("\n텍스트 응답 결과:")
    print(f"상태: {text_result['status']}")
    print(f"목적: {text_result['purpose']}")
    
    if text_result['status'] == 'success':
        print("\n생성된 텍스트 응답:")
        print(text_result['response_text'])
    else:
        print(f"\n텍스트 응답 생성 에러: {text_result.get('error', '알 수 없는 에러')}")

if __name__ == "__main__":
    test_image_and_text_generation() 