import json
import re
import os 
from openai import OpenAI
from clickdiffusion.plotting import visualize_scene_graph


# access api key env variable
api_key = os.environ.get("API_KEY")

client = OpenAI(
    api_key=api_key
)

def follow_instruction(input_scene_graph, preamble_prompt, icl_prompt, instruction_prompt, seed=1):
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system", 
                "content": str(preamble_prompt)
            },
            {
                "role": "user",
                "content": str(icl_prompt) + str(instruction_prompt)
            },
        ],
        seed=seed,
    )
    # print(f"Pre-amble prompt: {preamble_prompt}")
    # print(f"ICL prompt: {icl_prompt}")
    # print(f"Instruction prompt: {instruction_prompt}")
    # print(f"Response: {response}")
    transformed_response = response.choices[0].message.content
    # print(f"Transformed response: {transformed_response}")
    # Parse json to python dict
    transformed_response = json.loads(transformed_response)
    # print(f"Transformed response: {transformed_response}")
    output_scene_graph = transformed_response
    # raise Exception("Stop here")
    # Extract the scene graph from the response 
    # Regex code between {}
    # transformed_response = transformed_response.replace("\n", "")
    # pattern = r"\{([^{}]*)\}"
    # Use re.search to find the first match
    # match = re.search(pattern, transformed_response)
    # assert match, "No scene graph found in response: {}".format(response)
    # scene_graph_string = match.group(1)
    # print(f"Preamble prompt: {preamble_prompt}")
    # print(f"ICL prompt: {icl_prompt}")
    # print(f"Instruction prompt: {instruction_prompt}")
    # print(f"Transformed response: {transformed_response}")
    # TODO Use something more sustainable like Outlines? to enable guarantees for structured output. 
    # json_match = re.search(r'{.*}', transformed_response)
    # scene_graph_string = json_match.group(0)
    # start_index = transformed_response.find("{'prompt':")
    # end_index = transformed_response.find("]}") + 2  # Include the closing curly brace and square bracket
    # scene_graph_string = transformed_response[start_index:end_index]
    # print(f"Scene graph string: {scene_graph_string}")
    # Parse the response into a scene graph
    # output_scene_graph = eval(scene_graph_string)

    return output_scene_graph

if __name__ == "__main__":
    example_scene_graph = {
        "boxes": {
            {"name": "dog", "box": [0.2, 0.3, 0.5, 0.7]},
            {"name": "tree", "box": [0.4, 0.8, 0.2, 0.2]}
        },
        "prompt": "A dog by a tree."
    }
    # Run the instruction following
    output_scene_graph = follow_instruction(example_scene_graph, "Move the dog to the right of the tree.")
    # Visualize the changed scene graph
    visualize_scene_graph(output_scene_graph, save_path="output_scene_graph.png")