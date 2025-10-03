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
	'HF_TOKEN': 'HF_TOKEN_KEY'
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
hyperparameters={
    'do_train': True,
    'do_eval': False,
    'learning_rate': 2e-5,
    'model_name_or_path': 'meta-llama/Llama-3.1-8B-Instruct',
    'train_file': '/opt/ml/input/data/train/train.txt',
    'evaluation_strategy': 'epoch',
    'save_strategy': 'epoch',
    'fp16': True,
    'num_train_epochs': 2,
    'per_device_train_batch_size': 1,
    'per_device_eval_batch_size': 1,
    'overwrite_output_dir': True,
    'output_dir': '/opt/ml/model',
    'logging_dir': '/opt/ml/output/logs',
    'tokenizer_name': 'meta-llama/Llama-3.1-8B-Instruct',
    'block_size': 512,
}

# Git configuration for Hugging Face training script
git_config = {'repo': 'https://github.com/huggingface/transformers.git', 'branch': 'v4.36.0'}

huggingface_estimator = HuggingFace(
    entry_point='run_clm.py',
    source_dir='./examples/pytorch/language-modeling',
    instance_type='ml.g5.2xlarge',
    instance_count=1,
    role=role,
    git_config=git_config,
    transformers_version='4.36.0',
    pytorch_version='2.1.0',
    py_version='py310',
    hyperparameters=hyperparameters
)

huggingface_estimator.fit({'train': 's3://braxton-llm-bucket/opt/ml/input/data/train/'})
