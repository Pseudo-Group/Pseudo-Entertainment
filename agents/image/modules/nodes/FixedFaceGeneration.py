import os
import json
import asyncio
import websockets

from agents.base_node import BaseNode
from agents.image.modules.models import get_gemini_model
from agents.image.modules.chains import set_comfyui_generation_chain


class FixedFaceGenerationNode(BaseNode):
    """
    고정된 이미지를 사용하여 Prompt에 맞게 새로운 이미지를 생성하는 노드
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = get_gemini_model()
        self.chain = set_comfyui_generation_chain()

    async def execute(self, state):
        """
        LangGraph에서 비동기 노드로 호출될 때 실행되는 함수
        """
        return await self.execute_async(state)

    async def set_payload(self, state):
        """
        ComfyUI에 요청하는 Payload를 생성합니다.
        """
        response = await self.chain.ainvoke({
            "persona": state['persona']
        })

        payload = {
            "tool": "generate_image",
            "params": json.dumps({
                "image": os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    '..', 'comfyui_server', 'ComfyUI', 'input', 'save_fixed_image.png'
                ),
                "prompt": 'fcsks fxhks fhyks, ' + response.get('prompt', ''),
                "negative_prompt": response.get('negative_prompt', ''),
                "width": 512,
                "height": 512,
                "workflow_id": "hyperlora_face_generation",
            })
        }
        return payload

    async def execute_async(self, state):
        """
        WebSocket을 통해 ComfyUI MCP 서버와 통신하고 응답을 반환합니다.
        """
        url = "ws://localhost:9000"
        payload = await self.set_payload(state)

        try:
            async with websockets.connect(url) as ws:
                print("Connected to MCP server")
                await ws.send(json.dumps(payload))
                response = await ws.recv()
                print("Response from server:")
                return json.loads(response)
        except Exception as e:
            print(f"WebSocket error: {e}")
            return {"error": str(e)}