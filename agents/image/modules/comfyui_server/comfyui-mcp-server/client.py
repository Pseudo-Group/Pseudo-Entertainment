import asyncio
import websockets
import json

payload = {
    "tool": "generate_image",
    "params": json.dumps({
        "image": "try_01.png",
        "prompt": "fcsks fxhks fhyks, a young woman, wearing a wedding dress, standing at a church entrance, looking forward, photorealistic",
        "negative_prompt": "nsfw, lowres, bad anatomy, text, watermark, blurry, cropped",
        "width": 512,
        "height": 512,
        "workflow_id": "hyperlora_face_generation",
    })
}

async def test_mcp_server():
    uri = "ws://localhost:9000"
    try:
        async with websockets.connect(uri) as ws:
            print("Connected to MCP server")
            await ws.send(json.dumps(payload))
            response = await ws.recv()
            print("Response from server:")
            print(json.dumps(json.loads(response), indent=2))
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    print("Testing MCP server with WebSocket...")
    asyncio.run(test_mcp_server())