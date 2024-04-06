import torch
import PIL

from precise_editing.generation import InpaintAndUpscale
from diffusers import StableDiffusionGLIGENTextImagePipeline, StableDiffusionXLImg2ImgPipeline, AutoPipelineForText2Image, LCMScheduler
from diffusers.utils import load_image
import os

class InpaintAndUpscale():
    """
        A class to inpaint and upscale an image using the Stable Diffusion models.
    """

    def __init__(self, model_dir, use_lcm=True):
        # Make sub model paths
        gligen_path = os.path.join(model_dir, "gligen")
        refiner_path = os.path.join(model_dir, "upscaler")
        sdxl_path = os.path.join(model_dir, "single_object_model")
        lcm_adapter_path = os.path.join(model_dir, "lcm_adapter/pytorch_lora_weights.safetensors")
        # Load up each model 
        self.gligen_pipe = StableDiffusionGLIGENTextImagePipeline.from_pretrained(
            gligen_path,
            torch_dtype=torch.float16
        ).to("cuda")
        self.upscaler = StableDiffusionXLImg2ImgPipeline.from_pretrained(
            refiner_path, 
            torch_dtype=torch.float16, 
            variant="fp16", 
            use_safetensors=True
        ).to("cuda")
        self.single_object_model = AutoPipelineForText2Image.from_pretrained(
            sdxl_path, 
            torch_dtype=torch.float16, 
            variant="fp16"
        )   
        self.single_object_model.scheduler = LCMScheduler.from_config(self.single_object_model.scheduler.config)
        self.single_object_model.to("cuda")
        # load and fuse lcm lora
        self.single_object_model.load_lora_weights(lcm_adapter_path)
        self.single_object_model.fuse_lora()

    def generate_object_image(self, prompt):
        """
            Generate an image for the given prompt.
        """
        prompt = "A photo-realistic image of a " + prompt + ". Full body."
        return self.single_object_model(
            prompt=prompt,
            negative_prompt="drawing, painting, crayon, sketch, graphite, impressionist, noisy, blurry, soft, deformed, ugly",
            guidance_scale=1.0,
            num_inference_steps=4,
        ).images[0]

def model_fn(model_dir):
    # Load model 
    model = InpaintAndUpscale(model_dir)
    return model

def predict_fn(data, model):
    # Unpack data
    inpaint_and_upscale = model
    # Compute geenrate an image
    with torch.no_grad():
        # Run the gligen inpainter
        # Load the background 
        background_image = PIL.Image.open("background.jpg")
        # Generate an object image
        object_image = model.generate_object_image("dog")
        # Generate the layout image
        model_output = model.generate_image(
            "a dog",
            background_image,
            ["dog"],
            [object_image],
            [[0.1, 0.1, 0.8, 0.8]],
        )
        image = model_output.images[0]

    # return dictonary, which will be json serializable
    return {"image": image}