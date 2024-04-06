cp -r code models/code 

cd models
# git clone https://huggingface.co/anhnct/Gligen_Inpainting_Text_Image
# git clone https://huggingface.co/anhnct/stabilityai/stable-diffusion-xl-refiner-1.0
# git clone https://huggingface.co/anhnct/stabilityai/stable-diffusion-xl-base-1.0
# git clone https://huggingface.co/latent-consistency/lcm-lora-sdxl

# Make the tarball
tar zcvf model.tar.gz *