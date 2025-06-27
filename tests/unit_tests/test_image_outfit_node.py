from agents.image.modules.nodes import generate_outfit_prompt_node


def test_outfit_prompt_node():
    state = {"query": "겨울 캠핑 룩", "response": []}
    result = generate_outfit_prompt_node(state)

    print("\n 생성된 outfit_prompt:\n", result["outfit_prompt"])
    assert "outfit_prompt" in result
    assert isinstance(result["outfit_prompt"], str)


test_outfit_prompt_node()
