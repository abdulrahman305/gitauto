# Standard imports
import sys
import time
import jwt
import json
import urllib.parse
from typing import Any

# Get PEM file path
if len(sys.argv) > 1:
    pem = sys.argv[1]
else:
    pem = input("Enter path of private PEM file: ")

# Get the Client ID
if len(sys.argv) > 2:
    client_id = sys.argv[2]
else:
    client_id = input("Enter your Client ID: ")

# Open PEM
with open(pem, 'rb') as pem_file:
    signing_key = pem_file.read()

payload = {
    # Issued at time
    'iat': int(time.time()),
    # JWT expiration time (10 minutes maximum)
    'exp': int(time.time()) + 600,
    
    # GitHub App's client ID
    'iss': client_id
}

# Create JWT
encoded_jwt = jwt.encode(payload, signing_key, algorithm='RS256')

print(f"JWT: {encoded_jwt}")

# Third-party imports
import sentry_sdk
from fastapi import FastAPI, Request
from mangum import Mangum
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

# Local imports
from config import GITHUB_WEBHOOK_SECRET, ENV, PRODUCT_NAME, UTF8
from scheduler import schedule_handler
from services.github.github_manager import verify_webhook_signature
from services.webhook_handler import handle_webhook_event

if ENV != "local":
    sentry_sdk.init(
        dsn="https://b7ca4effebf7d7825b6464eade11734f@o4506827828101120.ingest.us.sentry.io/4506865231200256",  # noqa
        environment=ENV,
        integrations=[AwsLambdaIntegration()],
        traces_sample_rate=1.0,
    )

# Create FastAPI instance and Mangum handler. Mangum is a library that allows you to use FastAPI with AWS Lambda.
app = FastAPI()
mangum_handler = Mangum(app=app)


# Here is an entry point for the AWS Lambda function. Mangum is a library that allows you to use FastAPI with AWS Lambda.
def handler(event, context):
    if "source" in event and event["source"] == "aws.events":
        schedule_handler(_event=event, _context=context)
        return {"statusCode": 200}

    return mangum_handler(event=event, context=context)


@app.post(path="/webhook")
async def handle_webhook(request: Request) -> dict[str, str]:
    content_type: str = request.headers.get(
        "Content-Type", "Content-Type not specified"
    )
    event_name: str = request.headers.get("X-GitHub-Event", "Event not specified")
    print("\n" * 3 + "-" * 70)
    print(f"Received event: {event_name} with content type: {content_type}")

    # Validate if the webhook signature comes from GitHub
    await verify_webhook_signature(request=request, secret=GITHUB_WEBHOOK_SECRET)

    # Process the webhook event but never raise an exception as some event_name like "marketplace_purchase" doesn't have a payload
    try:
        request_body: bytes = await request.body()
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error in reading request body: {e}")
        request_body = b""

    payload: Any = {}
    try:
        # First try to parse the body as JSON
        payload = json.loads(s=request_body.decode(encoding=UTF8))
    except json.JSONDecodeError:
        # If JSON parsing fails, treat the body as URL-encoded
        decoded_body: dict[str, list[str]] = urllib.parse.parse_qs(
            qs=request_body.decode(encoding=UTF8)
        )
        if "payload" in decoded_body:
            payload = json.loads(s=decoded_body["payload"][0])
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error in parsing JSON payload: {e}")

    await handle_webhook_event(event_name=event_name, payload=payload)
    return {"message": "Webhook processed successfully"}


@app.get(path="/")
async def root() -> dict[str, str]:
    return {"message": PRODUCT_NAME}
