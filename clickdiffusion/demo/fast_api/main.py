from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys

from PIL import Image
from io import BytesIO
import base64
import os
import asyncio
import json
import jsonschema
import traceback

from clickdiffusion.generation import InpaintAndUpscale    
from clickdiffusion.instruction_following import follow_instruction
import clickdiffusion.prompting
import clickdiffusion.plotting

################## Define the ObjectImageCache class ##################

#################### Helper ########################

def round_floats_in_dict(input_data, decimal_places=2):
    if isinstance(input_data, float):
        return round(input_data, decimal_places)
    elif isinstance(input_data, dict):
        rounded_dict = {}
        for key, value in input_data.items():
            rounded_dict[key] = round_floats_in_dict(value, decimal_places)
        return rounded_dict
    elif isinstance(input_data, list):
        rounded_list = []
        for item in input_data:
            rounded_list.append(round_floats_in_dict(item, decimal_places))
        return rounded_list
    else:
        return input_data

################## Load up the server ##################

print("Starting FastAPI server...")
app = FastAPI()

origins = ["*"]

# Make a lock for the cache
object_image_cache_lock = asyncio.Lock()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

################## Load up the models ##################

background_image_map = {
    "park": "images/backgrounds/park.png",
    "driveway": "images/backgrounds/driveway.jpeg",
    "kitchen_table": "images/backgrounds/kitchen_table.jpeg",
    "living_room_table": "images/backgrounds/living_room_table.jpeg",
    "park_table": "images/backgrounds/park_table.png",
    "backyard": "images/backgrounds/BackYard.jpeg",
}

inpaint_and_upscale = None
llm_pipeline = None 
object_image_cache = None

def startup_event():
    """Used to load expensive models"""
    print("Loading models ...")
    # Load up the model one time 
    global inpaint_and_upscale
    inpaint_and_upscale = InpaintAndUpscale()
    # Load up the Click Diffusion LLM Pipeline 
    # Load up the cache
    # global object_image_cache
    # # object_image_cache = ObjectImageCache()
    # object_image_cache.load_cache()

app.add_event_handler("startup", startup_event)

################## Instruction following function ##################

def make_instruction_following_function():
    """
        Make the instruction following function. 
    """
    # Load examples 
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

    def instruction_following_function(input_scene_graph, instruction):
        # Make the instruction prompt
        instruction_prompt = clickdiffusion.prompting.make_instruction_prompt(
            input_scene_graph,
            instruction
        )
        # Run the prompt
        output_scene_graph = follow_instruction(
            input_scene_graph,
            preamble_prompt,
            examples_prompt,
            instruction_prompt,
        )   
        return output_scene_graph
    
    return instruction_following_function

instruction_following_function = make_instruction_following_function()

################## Define the API routes ##################

@app.post("/generate_image")
async def send_json(data: dict):
    try:
        assert 'background' in data, "No background specified in the request."
        assert 'layout' in data, "No layout specified in the request."
        assert 'instruction' in data, "No instruction specified in the request."
        # Construct a call to the InpaintAndUpscale model based on the query
        print(data)
        background = data.get('background')
        # Make sure the background is in the background image map
        assert background in background_image_map, f"Background {background} not found in the background image map."
        layout = data.get('layout')
        instruction = data.get('instruction')
        reloaded = data.get("reload")
        # Check if instruction is empty
        if instruction == "":
            # Just generate an image from the layout, no LLM instruction following
            modified_scene_graph = layout
        else: 
            max_num_tries = 3
            num_tries = 0
            while num_tries < max_num_tries:
                try:
                    # NOTE: Try multiple times in case schema structure is wrong. 
                    # Run the instruction following LLM pipeline
                    modified_scene_graph = instruction_following_function(layout, instruction)
                    # Scene graph has the form:
                    # example_scene_graph_schema = {
                    #     "boxes": [
                    #         {"name": "dog", "box": {'x': 0.7, 'y': 0.6, 'width': 0.2, 'height': 0.3}, "unique_id": 0},
                    #         {"name": "tree", "box": {'x': 0.7, 'y': 0.6, 'width': 0.2, 'height': 0.3}, "unique_id": 1}
                    #     ],
                    #     "prompt": "A dog by a tree."
                    # }
                    # Check that the scene graph is valid
                    assert "boxes" in modified_scene_graph, "Scene graph does not have boxes."
                    assert "prompt" in modified_scene_graph, "Scene graph does not have a prompt."
                    assert isinstance(modified_scene_graph["boxes"], list), "Scene graph boxes is not a list."
                    for box in modified_scene_graph["boxes"]:
                        assert "name" in box, "Box does not have a name."
                        assert "box" in box, "Box does not have a box."
                        # assert "unique_id" in box, "Box does not have a unique_id."
                        assert isinstance(box["box"], dict), "Box box is not a dictionary."
                    break
                except Exception as e:
                    traceback.print_exc()
                    num_tries += 1
            if num_tries == max_num_tries:
                raise Exception("Instruction following failed.")
        # Check if the image exists already
        if not reloaded:
            layout_hash = hash(json.dumps(modified_scene_graph, sort_keys=True))
            image_path = f"images/assets/{background}_{layout_hash}.png"
            if os.path.exists(image_path):
                # Load the image from the file
                with open(image_path, "rb") as file:
                    image_bytes = file.read()
                img_base64 = base64.b64encode(image_bytes).decode("utf-8")
                # Return JSON response with image data
                json_data = {'image': img_base64, 'layout': modified_scene_graph}
                return JSONResponse(content=json_data)
        # Logging/Plotting
        # Plot the instruction, input scene graph, and output
        clickdiffusion.plotting.plot_instruction_example(
            instruction,
            layout,
            modified_scene_graph,
            save_path="logs/test_instruction_example.png"
        )
        # Load images for each object or generate them 
        images = []
        for box in modified_scene_graph["boxes"]:
            name = box["name"]
            file_name = f"images/assets/{background}_{name}.png"
            if os.path.exists(file_name):
                image = Image.open(file_name)
            else: 
                image = inpaint_and_upscale.generate_object_image(name)
                image.save(file_name)
            image = image.convert("RGB")
            images.append(image)
        # images = [inpaint_and_upscale.generate_object_image(box["name"]) for box in modified_scene_graph["boxes"]]
        # Load the bounding boxes
        boxes = list(map(lambda box: box["box"], modified_scene_graph["boxes"]))
        boxes = list(map(lambda box: [box["x"], box["y"], box["x"] + box["width"], box["y"] + box["height"]], boxes)) # Convert bounding boxes to list of lists
        # Load the background image 
        background_image_path = background_image_map[background]
        background_image = Image.open(background_image_path)
        # Generate the phrases from the scene graph/layout
        phrases = list(map(lambda box: box["name"], modified_scene_graph["boxes"]))
        # Now run the inpaint and upscale model
        assert len(phrases) == len(images) == len(boxes), "Lengths of phrases, images, and boxes do not match."
        print(f"Phrases: {phrases}")
        print(f"Boxes: {boxes}")
        edited_image = inpaint_and_upscale.generate_image(
            prompt=modified_scene_graph["prompt"],
            background_image=background_image,
            phrases=phrases,
            images=images,
            boxes=boxes,
        )
        # Save the PIL image into the byte stream
        image_bytesio = BytesIO()
        edited_image.save(image_bytesio, format='PNG')  # Adjust the format as needed
        image_byte_array = image_bytesio.getvalue()
        img_base64 = base64.b64encode(image_byte_array).decode("utf-8")
        # Cache the image by hashing the layout
        modified_scene_graph = round_floats_in_dict(modified_scene_graph)
        hashed_dict = hash(json.dumps(modified_scene_graph, sort_keys=True))
        print(f"Hashed dict: {hashed_dict}")
        edited_image.save(f"images/assets/{background}_{hashed_dict}.png")
        # Return JSON response with image data
        json_data = {'image': img_base64, 'layout': modified_scene_graph}

        return JSONResponse(content=json_data)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))