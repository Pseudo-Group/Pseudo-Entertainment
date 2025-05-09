import json
from urllib import request

#This is the ComfyUI api prompt format.

#If you want it for a specific workflow you can "enable dev mode options"
#in the settings of the UI (gear beside the "Queue Size: ") this will enable
#a button on the UI to save workflows in api format.

#keep in mind ComfyUI is pre alpha software so this format will change a bit.

#this is the one for the default workflow

def queue_prompt(prompt):
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req =  request.Request("http://localhost:8188/prompt", data=data)
    request.urlopen(req)


with open("workflows/basic_api_test.json", "r") as f:
    prompt = json.load(f)
    #set the text prompt for our positive CLIPTextEncode
    prompt["6"]["inputs"]["text"] = "beautiful scenery nature glass bottle landscape, purple galaxy bottle"

    #set the seed for our KSampler node
    prompt["3"]["inputs"]["seed"] = 5


    queue_prompt(prompt)