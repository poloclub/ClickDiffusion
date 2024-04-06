from diffusers import StableDiffusionGLIGENTextImagePipeline, StableDiffusionXLImg2ImgPipeline, AutoPipelineForText2Image, LCMScheduler
from diffusers.utils import load_image
import PIL
import torch

class InpaintAndUpscale():
    """
        A class to inpaint and upscale an image using the Stable Diffusion models.
    """

    def __init__(self, use_lcm=True):
        self.gligen_pipe = StableDiffusionGLIGENTextImagePipeline.from_pretrained(
            "anhnct/Gligen_Inpainting_Text_Image",
            torch_dtype=torch.float16
        ).to("cuda")

        self.upscaler = StableDiffusionXLImg2ImgPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-refiner-1.0", 
            torch_dtype=torch.float16, 
            variant="fp16", 
            use_safetensors=True
        ).to("cuda")
        self.use_lcm = use_lcm

        if self.use_lcm:
            model_id = "stabilityai/stable-diffusion-xl-base-1.0"
            adapter_id = "latent-consistency/lcm-lora-sdxl"
            self.single_object_model = AutoPipelineForText2Image.from_pretrained(
                model_id, 
                torch_dtype=torch.float16, 
                variant="fp16"
            )   
            self.single_object_model.scheduler = LCMScheduler.from_config(self.single_object_model.scheduler.config)
            self.single_object_model.to("cuda")
            # load and fuse lcm lora
            self.single_object_model.load_lora_weights(adapter_id)
            self.single_object_model.fuse_lora()
        else:
            self.single_object_model = AutoPipelineForText2Image.from_pretrained(
                "stabilityai/stable-diffusion-xl-base-1.0", 
                torch_dtype=torch.float16, 
                variant="fp16", 
                use_safetensors=True
            ).to("cuda")

    def generate_object_image(self, prompt):
        """
            Generate an image for the given prompt.
        """
        prompt = "A photo-realistic image of a " + prompt + ". Full body."
        if self.use_lcm:
            return self.single_object_model(
                prompt=prompt,
                negative_prompt="drawing, painting, crayon, sketch, graphite, impressionist, noisy, blurry, soft, deformed, ugly",
                guidance_scale=1.0,
                num_inference_steps=4,
            ).images[0]
        else: 
            return self.single_object_model(
                prompt=prompt,
                negative_prompt="drawing, painting, crayon, sketch, graphite, impressionist, noisy, blurry, soft, deformed, ugly",
            ).images[0]

    def generate_image(
        self,
        prompt: str,
        background_image: PIL.Image,
        phrases: list,
        images: list,
        boxes: list,
    ):
        """
            Generate an image by inpainting and upscaling the background image.
        """
        # Run the gligen inpainter
        images = self.gligen_pipe(
            prompt=prompt,
            gligen_phrases=phrases,
            gligen_inpaint_image=background_image,
            gligen_boxes=boxes,
            gligen_images=images,
            gligen_scheduled_sampling_beta=1,
            output_type="pil",
            guidance_scale=7.5,
            num_inference_steps=50,
        ).images[0]
        # Run the upscaler
        upscaled_image = self.upscaler(
            prompt=prompt,
            image=images,
            negative_prompt="drawing, painting, crayon, sketch, graphite, impressionist, noisy, blurry, soft, deformed, ugly",
            strength=0.2,
        ).images[0]

        return upscaled_image
