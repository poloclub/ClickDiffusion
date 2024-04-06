"""
    Tools for prompting
"""
import os
import json
import numpy as np
import re

split_files = {
    "train": "train_jsonified.json",
    "test": "test_jsonified.json",
}

class TextPrompt(object):
    """
        Wrapper container for text prompts
    """

    def __init__(self, prompt=""):
        self.prompt = prompt
        self.clean_prompt = self.clean_prompt(prompt)

    def clean_prompt(self, prompt):
        """
            Clean the prompt by removing extra whitespace and newlines
        """
        prompt = prompt.replace("\n", "") # Remove new lines
        prompt = prompt.replace("\t", "") # Remove tabs
        prompt = re.sub(r'\s+', ' ', prompt).strip()
        # prompt = prompt.strip() # Remove whitespace
        return prompt

    def __add__(self, other):
        """
            Add two text prompts together
        """
        return TextPrompt(self.prompt + other.prompt)

    def __iadd__(self, other):
        """
            Add two text prompts together
        """
        return TextPrompt(self.prompt + other.prompt)

    def __str__(self):
        return self.clean_prompt

    def __repr__(self):
        return self.clean_prompt

def randomly_perturb_prompt(prompt, perterb_percentage=0.1):
    """
        Randomly adjust the bounding box coordinates in an instruction prompt
        by a small amount.
    """
    def split_string(s):
        # Split the string using regular expressions
        # The pattern matches either a sequence of non-bracket characters or a sequence of characters inside brackets
        return re.findall(r'[^\[\]]+|\[.*?\]', s)
    # Isolate the bounding boxes in the prompt
    splits = split_string(prompt)
    for i, split in enumerate(splits):
        if split[0] == "[" and split[-1] == "]":
            box = eval(split)
            # Randomly perturb the box
            box = np.array(box)
            # Perterb width
            box[0] += np.random.uniform(
                -perterb_percentage, 
                perterb_percentage
            ) * np.abs(box[2] - box[0])
            box[2] += np.random.uniform(
                -perterb_percentage,
                perterb_percentage
            ) * np.abs(box[2] - box[0])
            # Perterb height
            box[1] += np.random.uniform(
                -perterb_percentage, 
                perterb_percentage
            ) * np.abs(box[3] - box[1])
            box[3] += np.random.uniform(
                -perterb_percentage, 
                perterb_percentage
            ) * np.abs(box[3] - box[1])
            # Convert back to string
            box_string = "["
            for box_index, num in enumerate(box):
                box_string += f"{num:.2f}"
                if box_index < len(box) - 1:
                    box_string += ", "
            box_string += "]"
            splits[i] = box_string
    # Join the splits back together
    perturbed_prompt = "".join(splits)

    return perturbed_prompt

def generate_in_context_learning_prompt(num_examples, chain_of_thought=True, perterbation=True, split="train"):
    """
        Generates a prompt for instruction following that 
        puts examples pulled from one of the splits in context
        to allow the model to learn from annotated examples
        without the need for fine-tuning. 
    """
    # Load the json examples
    assert split in split_files.keys(), f"Split {split} not found in {split_files.keys()}"
    examples_path = os.path.join(
        os.environ["EDITING_EXAMPLES"],
        split_files[split],
    )
    with open(examples_path) as f:
        examples = json.load(f)['examples']
    # Select number of examples
    if num_examples == "all":
        num_examples = len(examples)
    # Preamble: the first part of the prompt
    preamble = TextPrompt(
        """
            Your job is to read a user's instructions for how to change a scene graph
            which represents the layout of an artistic composition. The scene graph
            contains a text prompt describing the image, and a dictionary of 
            objects in the image and bounding boxes for each object. The user's 
            instruction will tell you how to manipulate the objects in the scene graph.
            Your job is to generate this output scene graph in the form of a json 
            object. If you are not sure or you think the instruction is ambiguous, 
            just make your best guess. If the instructin is impossible to follow,
            just don't change the scene graph. 

            The types of operations will be things like adding objects, moving objects, removing objects,
            changing their appearance, and changing their size. You may also see composite 
            edits that combine multiple of these categories. The procedure you want to take is
            1. Read the input scene graph and instruction
            2. Generate a chain of thought that describes how you would follow the instruction, 
                deciding which type of edit it is, which objects it impacts, and how 
                those objects change. 
            3. Generate the output scene graph that follows the instruction
            
            Generate a json object with the following schema:
            {
                'chain_of_thought': 'Chain of thought will go here',
                'prompt': 'text describing the image',
                'boxes': [
                    {
                        'name': 'object_name', 
                        'box': {
                            'x': 0.0, 
                            'y': 0.0, 
                            'width': 0.0, 
                            'height': 0.0
                        }
                    },
                    ...
                ],
            }
        """
    )
    # Examples: in context learning examples pasted into the context. 
    # Randomly sample num_examples examples
    examples_prompt = TextPrompt()
    example_indices = np.random.choice(len(examples), num_examples)
    examples = [examples[i] for i in example_indices]
    for example in examples:
        input_scene_graph = example["input_scene_graph"]
        instruction = example["instruction"]
        # Apply perterbation to the prompt
        if perterbation:
            instruction = randomly_perturb_prompt(instruction)
        output_scene_graph = example["output_scene_graph"]

        if chain_of_thought:
            example_chain_of_thought = example["chain_of_thought"]
            example_prompt = TextPrompt(
                f"""
                    Input Scene Graph: {input_scene_graph}
                    Instruction: '{instruction}'
                    Chain of Thought: {example_chain_of_thought}
                    Output Scene Graph: {output_scene_graph}
                """
            )
        else:
            example_prompt = TextPrompt(
                f"""
                    Input Scene Graph: {input_scene_graph}
                    Instruction: '{instruction}'
                    Output Scene Graph: {output_scene_graph}
                """
            )

        examples_prompt += example_prompt
    # Piece everything together
    final_prompt = preamble + examples_prompt

    return preamble, examples_prompt

def make_instruction_prompt(input_scene_graph, instruction, chain_of_thought=True):
    """
        Prompt for the instruction following task.
    """

    prompt = TextPrompt(
        f"""
            Input Scene Graph: {input_scene_graph}
            Instruction: '{instruction}'
            Chain of Thought:
        """
    )

    return prompt