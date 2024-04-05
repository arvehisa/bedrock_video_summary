import boto3
import json
import logging
import os

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def read_prompt():
    """Reads the prompt text from 'prompt.txt'."""
    with open("prompt.txt", "r", encoding="utf-8") as file:
        return file.read()
    
def read_system_prompt():
    with open("system_prompt.txt", "r", encoding="utf-8") as file:
        return file.read()

def generate_message(bedrock_runtime, model_id, system_prompt, messages, max_tokens):
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": messages
    })
    response = bedrock_runtime.invoke_model(body=body, modelId=model_id)
    response_body = json.loads(response.get('body').read())
    return response_body

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('videosum-table')  # Corrected table name

    try:
        # Retrieve the S3 URL from the event object
        s3_uri = event['Payload']['s3_uri']  # Ensure this key exists in your event object

        # Retrieve the transcription text from DynamoDB
        response = table.get_item(Key={'s3_uri': s3_uri})
        if 'Item' not in response:
            return {'statusCode': 404, 'body': json.dumps('Transcription not found in DynamoDB.')}
        sum_en = response['Item']['sum_en']  # Assuming this is the correct key

        # Prepare the prompt
        system_prompt = read_system_prompt()
        prompt = read_prompt().replace("{transcript_text}", sum_en)

        bedrock_runtime = boto3.client(service_name='bedrock-runtime')
        model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
        max_tokens = 4000

        # Prepare messages for the API call
        user_message = {"role": "user", "content": prompt}
        messages = [user_message]

        # Generate the message
        response = generate_message(bedrock_runtime, model_id, system_prompt, messages, max_tokens)

        # Assuming 'response' contains a 'content' list with at least one item, and its 'text' key has the summary
        sum_ja = response['content'][0]['text']  # Check if this matches the actual response structure

        # Update the DynamoDB item with the summary
        update_response = table.update_item(
            Key={'s3_uri': s3_uri},
            UpdateExpression='SET sum_ja = :val',
            ExpressionAttributeValues={':val': sum_ja}
        )

        return {
            'statusCode': 200,
            's3_uri': s3_uri,
            'body': json.dumps({'summary': sum_ja}, ensure_ascii=False)
        }

    except ClientError as err:
        message = err.response["Error"]["Message"]
        logger.error("A client error occurred: %s", message)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': message})
        }
