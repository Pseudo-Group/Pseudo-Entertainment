"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.
"""
import os
import base64
import logging

from PIL import Image
from io import BytesIO

from agents.base_node import BaseNode

from agents.image.modules.chains import set_face_generation_chain
from agents.image.modules.models import get_gemini_model
# from agents.image.modules.chains import set_image_generation_chain

class NewFaceGenerationNode(BaseNode):
    """
    고정된 얼굴 생성을 위한 노드
    
    이 노드는 Text Agent의 Extracted Persona를 사용하여 페르소나에 맞는 얼굴 이미지를 생성합니다.
    생성된 이미지는 ComfyUI에 전달되어 최종 이미지로 사용됩니다.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chain = set_face_generation_chain()

    def execute(self, state):
        """
        주어진 state에서 Query를 추출하여
        이미지 생성 체인에 전달하고, 결과를 응답으로 반환한다.
        
        Args:
            state: 현재 워크플로우 상태
        Returns:
            dict: 생성된 이미지 정보가 포함된 응답
        """
        tries = 5

        while tries > 0:
            response = self.chain.invoke({
                "persona" : state['persona'],
            })

            if response.response_metadata.get('finish_reason') == 'IMAGE_SAFETY':
                # 이미지 안전성 문제로 인해 재시도
                tries -= 1
                logging.warning(f"Image generation failed due to safety issue. Remaining tries: {tries}")
                continue
            else:
                # 이미지 생성 성공
                break
        else:
            # 모든 시도에서 실패한 경우
            logging.error("Image generation failed after multiple attempts.")
            return {"response": "이미지 생성에 실패했습니다."}
        
        ## Save image - ComfyUI Input 경로
        image_path = os.path.abspath(os.path.join("agents/image/modules/comfyui_server/ComfyUI/input", "fixed_image.png"))
        image = Image.open(BytesIO(base64.b64decode(response.content[-1].get('image_url').get('url').split(',')[-1])))
        image.save(image_path)
        logging.info(f"Image saved at {image_path}")

        # 응답 반환
        return {
            "fixed" : True,
            "fixed_image" : response.content[-1].get('image_url').get('url').split(',')[-1],
            "fixed_image_path" : image_path,
        }
