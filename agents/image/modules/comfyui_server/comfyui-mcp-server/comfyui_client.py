import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ComfyUIClient")

DEFAULT_MAPPING = {
    "prompt": ("6", "text"),
    "width": ("5", "width"),
    "height": ("5", "height"),
    "model": ("4", "ckpt_name")
}

class ComfyUIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.available_models = self._get_available_models()

    def _get_available_models(self):
        """Fetch list of available checkpoint models from ComfyUI"""
        try:
            response = requests.get(f"{self.base_url}/object_info/CheckpointLoaderSimple")
            if response.status_code != 200:
                logger.warning("Failed to fetch model list; using default handling")
                return []
            data = response.json()
            models = data["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
            logger.info(f"Available models: {models}")
            return models
        except Exception as e:
            logger.warning(f"Error fetching models: {e}")
            return []

    def generate_image(self, prompt, width, height, workflow_id="basic_api_test", model=None):
        try:
            workflow_file = f"workflows/{workflow_id}.json"
            with open(workflow_file, "r") as f:
                workflow = json.load(f)

            params = {"prompt": prompt, "width": width, "height": height}
            if model:
                # Validate or correct model name
                if model.endswith("'"):  # Strip accidental quote
                    model = model.rstrip("'")
                    logger.info(f"Corrected model name: {model}")
                if self.available_models and model not in self.available_models:
                    raise Exception(f"Model '{model}' not in available models: {self.available_models}")
                params["model"] = model

            for param_key, value in params.items():
                if param_key in DEFAULT_MAPPING:
                    node_id, input_key = DEFAULT_MAPPING[param_key]
                    if node_id not in workflow:
                        raise Exception(f"Node {node_id} not found in workflow {workflow_id}")
                    workflow[node_id]["inputs"][input_key] = value

            logger.info(f"Submitting workflow {workflow_id} to ComfyUI...")
            response = requests.post(f"{self.base_url}/prompt", json={"prompt": workflow})
            if response.status_code != 200:
                raise Exception(f"Failed to queue workflow: {response.status_code} - {response.text}")

            prompt_id = response.json()["prompt_id"]
            logger.info(f"Queued workflow with prompt_id: {prompt_id}")

            max_attempts = 30
            for _ in range(max_attempts):
                history = requests.get(f"{self.base_url}/history/{prompt_id}").json()
                if history.get(prompt_id):
                    outputs = history[prompt_id]["outputs"]
                    logger.info("Workflow outputs: %s", json.dumps(outputs, indent=2))
                    image_node = next((nid for nid, out in outputs.items() if "images" in out), None)
                    if not image_node:
                        raise Exception(f"No output node with images found: {outputs}")
                    image_filename = outputs[image_node]["images"][0]["filename"]
                    image_url = f"{self.base_url}/view?filename={image_filename}&subfolder=&type=output"
                    logger.info(f"Generated image URL: {image_url}")
                    return image_url
                time.sleep(1)
            raise Exception(f"Workflow {prompt_id} didn’t complete within {max_attempts} seconds")

        except FileNotFoundError:
            raise Exception(f"Workflow file '{workflow_file}' not found")
        except KeyError as e:
            raise Exception(f"Workflow error - invalid node or input: {e}")
        except requests.RequestException as e:
            raise Exception(f"ComfyUI API error: {e}")