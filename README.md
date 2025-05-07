Deploying and Training of Llama 3.1-8B-Instruct on Amazon SageMaker (not locally)

There are multiple ways to deploy Llama 3.1-8B-Instruct. Today we are going through 2 methods:
1. Deploying Llama 3.1-8B-Instruct in SageMaker through Hugging Face Hub
2. Deploying Llama 3.1-8B-Instruct in SageMaker using a model artifact

📘 README: Deploying and Testing a LLaMA Model with AWS Lambda + API Gateway + Frontend
🔧 Overview
This project demonstrates how to deploy a Meta LLaMA 3.1 8B Instruct model using Amazon SageMaker JumpStart, expose it through a Lambda function and API Gateway, and connect it to a simple HTML frontend.

📌 Stack Components
SageMaker — Model deployment (LLaMA 3.1 8B Instruct)

AWS Lambda — Serverless backend to invoke model

API Gateway (HTTP API) — Public-facing API endpoint

HTML + JS Frontend — Lightweight test interface

🚀 Step-by-Step Setup
✅ 1. Deploy the Model via SageMaker JumpStart
Go to the AWS Console → SageMaker → JumpStart

Search for "LLaMA 3.1 8B Instruct"

Click Deploy

Wait for the endpoint to be active

Copy the endpoint name (e.g., jumpstart-dft-meta-textgeneration-llama-3b...)

✅ 2. Create the Lambda Function
Go to AWS Lambda Console

Click Create Function

Name: SageMakerInvokeFunction

Runtime: Python 3.11

Permissions: “Create new role with basic Lambda permissions”

Replace the default code with:

python
Copy
import boto3
import json

sagemaker = boto3.client('sagemaker-runtime')
ENDPOINT_NAME = 'your-sagemaker-endpoint-name'  # 🔁 Replace this

def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "")

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
Click Deploy

Go to Configuration → Permissions, and click the execution role

Attach the policy:

nginx
Copy
AmazonSageMakerFullAccess
✅ 3. Create HTTP API in API Gateway
Go to API Gateway > HTTP APIs

Click Create API

Integration: Lambda → SageMakerInvokeFunction

Route:

Method: ANY

Path: /chat

Go to CORS settings (left sidebar)

Allowed Origins: *

Allowed Methods: OPTIONS,POST

Allowed Headers: content-type

Go to Deployments → Deploy to $default stage

Copy your API URL:

bash
Copy
https://your-api-id.execute-api.us-east-1.amazonaws.com/chat
✅ 4. Create the Frontend Test Site
Create a file called test.html:

html
Copy
<!DOCTYPE html>
<html>
<head>
  <title>LLM Test Frontend</title>
</head>
<body>
  <h2>Talk to the Model</h2>
  <textarea id="userInput" rows="4" cols="50" placeholder="Type your message here..."></textarea><br>
  <button onclick="sendToModel()">Send</button>

  <h3>Model Response:</h3>
  <pre id="responseBox">Waiting for input...</pre>

  <script>
    async function sendToModel() {
      const input = document.getElementById("userInput").value;
      const responseBox = document.getElementById("responseBox");
      responseBox.textContent = "Sending request...";

      try {
        const res = await fetch("https://your-api-id.execute-api.us-east-1.amazonaws.com/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ input: input })
        });

        const data = await res.json();
        responseBox.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        console.error(err);
        responseBox.textContent = "Error: " + err.message;
      }
    }
  </script>
</body>
</html>
🔁 Replace the fetch() URL with your actual API Gateway endpoint.

✅ Result
You can now:

Type a message in the browser

Send it to the deployed LLaMA model

See the model’s response in real time

✅ Optional Improvements
✅ Add a chat-style UI

🔐 Secure your API with API keys or Cognito

🚀 Host your frontend using S3 static hosting or GitHub Pages

🔁 Log input/output in DynamoDB for auditing
