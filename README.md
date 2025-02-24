# llm-deployment-aws-sagemaker

Initial script
import json
import sagemaker
import boto3
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri

try:
	role = sagemaker.get_execution_role()
except ValueError:
	iam = boto3.client('iam')
	role = iam.get_role(RoleName='sagemaker_execution_role')['Role']['Arn']

# Hub Model configuration. https://huggingface.co/models
hub = {
	'HF_MODEL_ID':'meta-llama/Llama-3.1-8B-Instruct',
	'SM_NUM_GPUS': json.dumps(1),
	'HF_TOKEN': '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'
}

assert hub['HF_TOKEN'] != '<REPLACE WITH YOUR TOKEN>', "You have to provide a token."

# create Hugging Face Model Class
huggingface_model = HuggingFaceModel(
	image_uri=get_huggingface_llm_image_uri("huggingface",version="3.0.1"),
	env=hub,
	role=role, 
)

# deploy model to SageMaker Inference
predictor = huggingface_model.deploy(
	initial_instance_count=1,
	instance_type="ml.g5.4xlarge",
	container_startup_health_check_timeout=900,
  )

Once deployed
# send request with output length limit
response = predictor.predict({
    "inputs": "Hello!",
    "parameters": {
        "max_new_tokens": 50  # Set the maximum number of tokens to generate
    }
})

print(response)

