Deploying and Training of Llama 3.1-8B-Instruct on Amazon SageMaker (not locally)

There are multiple ways to deploy Llama 3.1-8B-Instruct. Today we are going through 2 methods:
1. Deploying Llama 3.1-8B-Instruct in SageMaker through Hugging Face Hub
2. Deploying Llama 3.1-8B-Instruct in SageMaker using a model artifact

# 🦙 Deploy and Test LLaMA 3.1 8B Instruct on AWS

This guide walks you through deploying **Meta’s LLaMA 3.1 8B Instruct** model using Amazon SageMaker, exposing it via **AWS Lambda + API Gateway**, and testing it using a simple **HTML frontend**.

---

## 📦 What You’ll Build

- ✅ Deployed LLaMA model via **SageMaker JumpStart**
- ✅ A serverless **Lambda function** to invoke the model
- ✅ A public **HTTP API** with **CORS** enabled
- ✅ A frontend webpage to test the model

---

## 🚀 Deployment Overview

### ✅ 1. Deploy LLaMA 3.1 via SageMaker JumpStart

1. Open **SageMaker Console → JumpStart**
2. Search for **“LLaMA 3.1 8B Instruct”**
3. Click **Deploy**
4. Wait until the endpoint is live
5. Copy the endpoint name (e.g., `jumpstart-dft-meta-textgeneration-llama-3b-*`)

---

### ✅ 2. Create the Lambda Function

1. Go to **AWS Lambda Console**
2. Create a function:
   - Name: `SageMakerInvokeFunction`
   - Runtime: `Python 3.11`
   - Permissions: Create new role with basic Lambda permissions

3. Paste this code and **replace** the `ENDPOINT_NAME`:

```python
import boto3, json

sagemaker = boto3.client('sagemaker-runtime')
ENDPOINT_NAME = 'your-sagemaker-endpoint-name'

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
```

4. Click **Deploy**
5. Go to **Configuration > Permissions**
6. Click the role name and attach:  
   `AmazonSageMakerFullAccess`

---

### ✅ 3. Set Up HTTP API Gateway

1. Go to **API Gateway > HTTP APIs**
2. Create a new API with:
   - Integration: Lambda → `SageMakerInvokeFunction`
   - Route:
     - Method: `ANY`
     - Path: `/chat`

3. Under **CORS**: (NOTE: SKIP THIS STEP IF YOU'RE USING MY LAMBDA FUNCTION FILE)
   - Origins: `*`
   - Methods: `POST, OPTIONS`
   - Headers: `content-type`

4. Go to **Deployments > Deploy to $default stage**
5. Copy your endpoint URL (e.g.):
   ```
   https://your-api-id.execute-api.us-east-1.amazonaws.com/chat
   ```

---

### ✅ 4. Create the Frontend Test Page

Make a file called `test.html`:

```html
<!DOCTYPE html>
<html>
<head><title>LLM Test</title></head>
<body>
  <h2>Talk to LLaMA</h2>
  <textarea id="userInput" rows="4" cols="50" placeholder="Ask me something..."></textarea><br>
  <button onclick="sendToModel()">Send</button>
  <h3>Model Response:</h3>
  <pre id="responseBox">Waiting for input...</pre>

  <script>
    async function sendToModel() {
      const input = document.getElementById("userInput").value;
      const responseBox = document.getElementById("responseBox");
      responseBox.textContent = "Sending...";

      try {
        const res = await fetch("https://your-api-id.execute-api.us-east-1.amazonaws.com/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ input })
        });
        const data = await res.json();
        responseBox.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        responseBox.textContent = "Error: " + err.message;
      }
    }
  </script>
</body>
</html>
```

> 🔁 Replace the fetch URL with your actual API endpoint

---

## ✅ Test It

- Open `test.html` in your browser
- Type a message like `What’s the capital of France?`
- Click **Send**
- You’ll see the model’s JSON response in the browser

## Test in Console
```bash
curl -X OPTIONS https://your-api-id.execute-api.us-east-1.amazonaws.com/chat \
  -H "Origin: null" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" -i
```

- Output should look like:
  
- HTTP/2 200 
- date: Wed, 07 May 2025 15:24:39 GMT
- content-length: 0
- access-control-allow-origin: *
- access-control-allow-methods: POST,OPTIONS
- access-control-allow-headers: content-type
- apigw-requestid: KNAwohhpIAMEVwA=

---

## 💡 Optional Improvements

- Add chat history + timestamps
- Host the frontend via GitHub Pages or S3
- Secure API with API key or Cognito
- Log requests/responses in DynamoDB

---
