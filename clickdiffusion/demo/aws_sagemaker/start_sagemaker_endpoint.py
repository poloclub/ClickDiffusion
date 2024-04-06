from sagemaker.huggingface import HuggingFaceModel
import sagemaker
import boto3

role = "arn:aws:iam::471112682675:role/ClickDiffusion-Sagemaker"
sess = sagemaker.Session(boto3.session.Session(region_name="us-east-1"))
bucket = sess.default_bucket() # Set a default S3 bucket

# Upload the model tar ball 
s3_location=f"s3://{sess.default_bucket()}/custom_inference/click_diffusion/model.tar.gz"
s3.upload_file("models/model.tar.gz", sess.default_bucket(), "custom_inference/click_diffusion/model.tar.gz")

# create Hugging Face Model Class
huggingface_model = HuggingFaceModel(
   model_data="s3://models/my-bert-model/model.tar.gz",  # path to your trained SageMaker model
   role=role,                                            # IAM role with permissions to create an endpoint
   transformers_version="4.26",                           # Transformers version used
   pytorch_version="1.13",                                # PyTorch version used
   py_version='py39',                                    # Python version used
)

# deploy model to SageMaker Inference
predictor = huggingface_model.deploy(
   initial_instance_count=1,
   instance_type="ml.m5.xlarge"
)

# example request: you always need to define "inputs"
data = {
   "inputs": "Camera - You are awarded a SiPix Digital Camera! call 09061221066 fromm landline. Delivery within 28 days."
}

# request
predictor.predict(data)