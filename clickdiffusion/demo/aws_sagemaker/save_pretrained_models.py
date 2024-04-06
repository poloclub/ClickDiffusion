import torch
from diffusers import StableDiffusionGLIGENTextImagePipeline, StableDiffusionXLImg2ImgPipeline, AutoPipelineForText2Image, LCMScheduler

gligen_pipe = StableDiffusionGLIGENTextImagePipeline.from_pretrained(
    "anhnct/Gligen_Inpainting_Text_Image",
    torch_dtype=torch.float16
).to("cuda")
upscaler = StableDiffusionXLImg2ImgPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-refiner-1.0", 
    torch_dtype=torch.float16, 
    variant="fp16", 
    use_safetensors=True
).to("cuda")
model_id = "stabilityai/stable-diffusion-xl-base-1.0"
# adapter_id = "latent-consistency/lcm-lora-sdxl"
single_object_model = AutoPipelineForText2Image.from_pretrained(
    model_id, 
    torch_dtype=torch.float16, 
    variant="fp16"
)   
# single_object_model.scheduler = LCMScheduler.from_config(single_object_model.scheduler.config)
# single_object_model.to("cuda")
# # load and fuse lcm lora
# single_object_model.load_lora_weights(adapter_id)
# single_object_model.fuse_lora()

# Save the models
gligen_pipe.save_pretrained("models/gligen")
upscaler.save_pretrained("models/upscaler")
single_object_model.save_pretrained("models/single_object_model")