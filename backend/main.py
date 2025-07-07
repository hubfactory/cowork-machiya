from fastapi import FastAPI
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv('AWS_REGION', 'ap-northeast-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'dummy'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'dummy'),
    endpoint_url=os.getenv('DYNAMODB_ENDPOINT_URL', 'http://dynamodb-local:8000')
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI + DynamoDB!"} 