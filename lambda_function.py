# This is the AWS Lambda function code
import boto3
import json

sagemaker = boto3.client('sagemaker-runtime')
ENDPOINT_NAME = 'llama3-endpoint'  # Replace with your endpoint name

def lambda_handler(event, context):
    print("Incoming event:", json.dumps(event))

    method = event.get("requestContext", {}).get("http", {}).get("method", "")

    # Strong CORS handling inside Lambda
    if method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
                "Access-Control-Allow-Headers": "content-type"
            }
        }

    try:
        body = json.loads(event["body"])
        user_input = body["input"]

        response = sagemaker.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType="application/json",
            Body=json.dumps({"inputs": user_input})
        )

        result = json.loads(response["Body"].read().decode())

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
                "Access-Control-Allow-Headers": "content-type",
                "content-type": "application/json"
            },
            "body": json.dumps({"response": result})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST,OPTIONS",
                "Access-Control-Allow-Headers": "content-type",
                "content-type": "application/json"
            },
            "body": json.dumps({"error": str(e)})
        }
