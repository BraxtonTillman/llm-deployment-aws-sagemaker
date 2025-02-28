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

# send request with output length limit
response = predictor.predict({
    "inputs": "Hello!",
    "parameters": {
        "max_new_tokens": 50  # Set the maximum number of tokens to generate
    }
})

print(response)



################## TRAINING ##################
import sagemaker
import boto3
from sagemaker.huggingface import HuggingFace

try:
	role = sagemaker.get_execution_role()
except ValueError:
	iam = boto3.client('iam')
	role = iam.get_role(RoleName='sagemaker_execution_role')['Role']['Arn']

# Define hyperparameters
hyperparameters = {
	'model_name_or_path':'meta-llama/Llama-3.1-8B-Instruct',
	'output_dir':'/opt/ml/model',
	'do_train': True,
	'do_eval': True,
	'num_train_epochs': 5,  # Increase since dataset is small
	'per_device_train_batch_size': 1,  # Prevent OOM errors
	'per_device_eval_batch_size': 1,
	'warmup_steps': 50,
	'save_strategy': 'epoch',
	'evaluation_strategy': 'epoch',
	'logging_dir': '/opt/ml/output/logs',
	'fp16': True,
	'overwrite_output_dir': True
}

# Git configuration for Hugging Face training script
git_config = {'repo': 'https://github.com/huggingface/transformers.git', 'branch': 'v4.37.0'}

# Hugging Face estimator for training
huggingface_estimator = HuggingFace(
	entry_point='run_clm.py',  # Use run_clm.py for chat model fine-tuning
	source_dir='examples/pytorch/language-modeling',  # Corrected path
	instance_type='ml.g5.2xlarge',  # Cheaper than P3 instances
	instance_count=1,
	role=role,
	git_config=git_config,
	transformers_version='4.36.0',
	pytorch_version='2.1.0',
	py_version='py310',
	hyperparameters=hyperparameters
)

# Start fine-tuning job
huggingface_estimator.fit({'train': 's3://braxton-llm-bucket/Norwich-PDS-InProgress (5)_20241129_192231_detailed 2.txt'})  # Upload file to S3 first!
