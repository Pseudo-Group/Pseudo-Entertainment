"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.
"""

import os
import base64
from datetime import datetime
from agents.base_node import BaseNode
from agents.image.modules.graphs import set_image_generation_graph, set_text_response_graph


class ImageGenerationNode(BaseNode):
    """
    이미지 생성을 위한 노드

    이 노드는 사용자의 요청에 따라 이미지를 생성하는 기능을 담당합니다.
    생성된 이미지는 지정된 디렉토리에 저장되며, base64 인코딩된 이미지 데이터도 함께 반환됩니다.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # BaseNode 초기화
        self.graph = set_image_generation_graph()  # 이미지 생성 체인 설정
        self.output_dir = os.path.join(os.getcwd(), "generated_images")
        os.makedirs(self.output_dir, exist_ok=True)

    def _save_image(self, image_base64: str, purpose: str) -> str:
        """
        Base64 인코딩된 이미지를 파일로 저장합니다.

        Args:
            image_base64: Base64 인코딩된 이미지 데이터
            purpose: 이미지 생성 목적 (파일명에 사용)

        Returns:
            str: 저장된 이미지의 경로
        """
        # 파일명 생성 (목적_타임스탬프.png)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{purpose}_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)

        # 이미지 데이터 디코딩 및 저장
        image_data = base64.b64decode(image_base64)
        with open(filepath, "wb") as f:
            f.write(image_data)

        return filepath

    def execute(self, state) -> dict:
        """
        주어진 상태(state)에서 query를 추출하여
        이미지 생성 체인에 전달하고, 결과를 응답으로 반환합니다.

        Args:
            state: 현재 워크플로우 상태

        Returns:
            dict: 생성된 이미지 정보가 포함된 응답
                - image_base64: Base64 인코딩된 이미지 데이터
                - image_path: 저장된 이미지 파일 경로
                - purpose: 이미지 생성 목적
                - text: 이미지 생성에 사용된 텍스트
        """
        try:
            # 이미지 생성
            image_base64 = self.graph.invoke(state)
            
            # 이미지 저장
            image_path = self._save_image(image_base64, state.get("purpose", "unknown"))

            # 결과 반환
            return {
                "image_base64": image_base64,
                "image_path": image_path,
                "purpose": state.get("purpose", ""),
                "text": state.get("text", ""),
                "status": "success"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "purpose": state.get("purpose", ""),
                "text": state.get("text", "")
            }


class TextResponseNode(BaseNode):
    """
    텍스트 응답을 처리하는 노드

    이 노드는 Gemini 모델의 텍스트 응답을 처리하고 관리하는 기능을 담당합니다.
    이미지 생성에 대한 설명이나 추가 정보를 텍스트로 제공합니다.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # BaseNode 초기화
        self.graph = set_text_response_graph()  # 텍스트 응답 체인 설정

    def execute(self, state) -> dict:
        """
        주어진 상태(state)에서 query를 추출하여
        텍스트 응답 체인에 전달하고, 결과를 응답으로 반환합니다.

        Args:
            state: 현재 워크플로우 상태

        Returns:
            dict: 텍스트 응답 정보가 포함된 응답
                - response_text: Gemini 모델의 텍스트 응답
                - purpose: 응답 생성 목적
                - text: 응답 생성에 사용된 텍스트
        """
        try:
            # 텍스트 응답 생성
            response_text = self.graph.invoke(state)

            # 결과 반환
            return {
                "response_text": response_text,
                "purpose": state.get("purpose", ""),
                "text": state.get("text", ""),
                "status": "success"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "purpose": state.get("purpose", ""),
                "text": state.get("text", "")
            }
