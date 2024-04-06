"""
    Test the in-context learning prompting on a test example. 
"""
import os
import json
import clickdiffusion.prompting
from clickdiffusion.instruction_following import follow_instruction
from clickdiffusion.plotting import plot_instruction_example

if __name__ == "__main__":
    # Load the example
    example_path = os.path.join(
        os.environ["EDITING_EXAMPLES"],
        "test_jsonified.json"
    )
    with open(example_path) as f:
        examples = json.load(f)
    examples = examples["examples"]
    # Make the prompt
    preamble_prompt, examples_prompt = clickdiffusion.prompting.generate_in_context_learning_prompt(
        "all",
        split="train"
    )
    # Iterate through the examples
    for example_index, example in enumerate(examples):
        # Make the instruction prompt
        instruction_prompt = clickdiffusion.prompting.make_instruction_prompt(
            example["input_scene_graph"],
            example["instruction"]
        )
        # Run the prompt
        output_scene_graph = follow_instruction(
            example["input_scene_graph"],
            preamble_prompt,
            examples_prompt,
            instruction_prompt,
        )
        # Visualize the output scene graph
        plot_instruction_example(
            example["instruction"],
            example["input_scene_graph"],
            output_scene_graph,
            save_path=f"images/test_instruction_example_{example_index}.png"
        )
