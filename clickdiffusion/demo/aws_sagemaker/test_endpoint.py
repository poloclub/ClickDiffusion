from sagemaker.huggingface.model import HuggingFaceModel

if __name__ == "__main__":
    # Load the endpoint 
    s3_location = ""
    role = ""
    # Create Hugging Face Model Class
    huggingface_model = HuggingFaceModel(
        model_data=s3_location,       # path to your model and script
        role=role,                    # iam role with permissions to create an Endpoint
        transformers_version="4.26",  # transformers version used
        pytorch_version="1.13",        # pytorch version used
        py_version='py39',            # python version used
    )
    # deploy the endpoint endpoint
    predictor = huggingface_model.deploy(
        initial_instance_count=1,
        instance_type="ml.g4dn.xlarge"
    )
    # Generate an image from a layout 
    data = {
        "inputs": "the mesmerizing performances of the leads keep the film grounded and keep the audience riveted .",
    }
    res = predictor.predict(data=data)
    print(res)
    # Save the image locally