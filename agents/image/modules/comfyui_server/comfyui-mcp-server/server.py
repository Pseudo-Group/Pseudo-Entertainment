import asyncio
import os
import json
import aiohttp
import logging
from typing import AsyncIterator
from contextlib import asynccontextmanager
import websockets
from mcp.server.fastmcp import FastMCP
from comfyui_client import ComfyUIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP_Server")

# Global ComfyUI client (fallback since context isn’t available)
comfyui_client = ComfyUIClient("http://localhost:8188")

# Define application context (for future use)
class AppContext:
    def __init__(self, comfyui_client: ComfyUIClient):
        self.comfyui_client = comfyui_client

# Lifespan management (placeholder for future context support)
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle"""
    logger.info("Starting MCP server lifecycle...")
    try:
        # Startup: Could add ComfyUI health check here in the future
        logger.info("ComfyUI client initialized globally")
        yield AppContext(comfyui_client=comfyui_client)
    finally:
        # Shutdown: Cleanup (if needed)
        logger.info("Shutting down MCP server")

# Initialize FastMCP with lifespan
mcp = FastMCP("ComfyUI_MCP_Server", lifespan=app_lifespan)

# Define the image generation tool
@mcp.tool()
def generate_image(params: str) -> dict:
    """Generate an image using ComfyUI"""
    logger.info(f"Received request with params: {params}")
    try:
        param_dict = json.loads(params)
        image = param_dict["image"]
        prompt = param_dict["prompt"]
        negative_prompt = param_dict.get("negative_prompt", None)
        width = param_dict.get("width", 512)
        height = param_dict.get("height", 512)
        workflow_id = param_dict.get("workflow_id", "basic_api_test")

        # Use global comfyui_client (since mcp.context isn’t available)
        image_url = comfyui_client.generate_image(
            image=image,
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            workflow_id=workflow_id,
        )
        logger.info(f"Returning image URL: {image_url}")
        return {"image_url": image_url}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": str(e)}

stop_event = asyncio.Event()
comfyui_process = None

# WebSocket server
async def handle_websocket(websocket):
    logger.info("WebSocket client connected")
    try:
        async for message in websocket:
            request = json.loads(message)
            logger.info(f"Received message: {request}")
            if request.get("tool") == "generate_image":
                result = await asyncio.to_thread(generate_image, request.get("params", ""))
                await websocket.send(json.dumps(result))
            elif request.get("command") == "shutdown":
                logger.info("Shutdown command received")
                stop_event.set()
                break
            else:
                await websocket.send(json.dumps({"error": "Unknown tool"}))
    except websockets.ConnectionClosed:
        logger.info("WebSocket client disconnected")

async def check_comfyui_health(timeout=20):
    url = "http://localhost:8188/"
    async with aiohttp.ClientSession() as session:
        for i in  range(timeout):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        logging.info("ComfyUI is connected")
                        return True
            except Exception as e:
                pass
            logging.info(f"ComfyUI not ready yet: {i * 5}s")
            await asyncio.sleep(5)
    raise TimeoutError("ComfyUI is not ready after 100 seconds")
            
# Main server loop
async def main():
    global comfyui_process

    logging.info("Launching ComfyUI server on port 8188...")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    python_path = os.path.abspath(os.path.join(BASE_DIR, "..", ".venv/bin/python"))
    comfyui_main_path = os.path.abspath(os.path.join(BASE_DIR, "..", "ComfyUI/main.py"))

    comfyui_process = await asyncio.create_subprocess_exec(
        python_path,
        comfyui_main_path,
        cwd=os.path.abspath(os.path.join(BASE_DIR, "..", "ComfyUI")),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        await check_comfyui_health(timeout=20)
    except TimeoutError as e:
        logging.error(f"Error: {str(e)}")
        comfyui_process.terminate()
        await comfyui_process.wait()
        return
    
    logging.info("ComfyUI server is running")
    logger.info("Starting MCP server on ws://localhost:9000...")
    async with websockets.serve(handle_websocket, "localhost", 9000, ping_interval=60, ping_timeout=300):
        await stop_event.wait()

    logging.info("MCP server is shutting down")

    if comfyui_process:
        comfyui_process.terminate()
        await comfyui_process.wait()
        logging.info("ComfyUI server terminated")

if __name__ == "__main__":
    asyncio.run(main())