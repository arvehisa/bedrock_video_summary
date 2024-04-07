import boto3
import json
import logging
from botocore.exceptions import ClientError
import math

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# need prompt file full path when do local test
def read_prompt():
    """Reads the prompt text from 'prompt.txt'."""
    with open("prompt.txt", "r", encoding="utf-8") as file:
        return file.read()
    
def read_system_prompt():
    with open("system_prompt.txt", "r", encoding="utf-8") as file:
        return file.read()

def split_transcript(transcript, lines_per_split=100):
    return [transcript[i:i+lines_per_split] for i in range(0, len(transcript), lines_per_split)]

def generate_message(bedrock_runtime, model_id, system_prompt, message, max_tokens):
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": message
    })
    response = bedrock_runtime.invoke_model(body=body, modelId=model_id)
    response_body = json.loads(response.get('body').read())
    return response_body.get('content', [])[0].get('text')

def extract_timestamp(line):
    timestamp = float(line.split(', ')[1])
    minutes = int(timestamp // 60)
    seconds = int(timestamp % 60)
    return f"{minutes} min {seconds} sec"

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('videosum-table')

    try:
        s3_uri = event['s3_uri']
        response = table.get_item(Key={'s3_uri': s3_uri})
        if 'Item' not in response:
            return {'statusCode': 404, 'body': json.dumps('Transcription not found in DynamoDB.')}

        transcript_formatted = response['Item']['transcript_formatted'].split('\n')
        sum_ja = response['Item'].get('sum_ja', '')  # DynamoDB から sum_ja を取得
        parts = split_transcript(transcript_formatted)
        
        bedrock_runtime = boto3.client(service_name='bedrock-runtime')
        model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
        system_prompt = read_system_prompt()
        max_tokens = 1000
        
        combined_response = []
        for part in parts:
            start_timestamp = extract_timestamp(part[0])
            part_text = "\n".join(part)
            prompt_template = read_prompt()
            prompt = prompt_template.replace("{ts_part}", part_text).replace("{sum_ja}", sum_ja)  # {ts_part} と {sum_ja} を置き換え
            message = [{"role": "user", "content": prompt}] 
            summary_part = generate_message(bedrock_runtime, model_id, system_prompt, message, max_tokens)
            print(summary_part)
            combined_response.append(f"[{start_timestamp}] {summary_part}")
        
        combined_summary = "\n".join(combined_response)
        update_response = table.update_item(
            Key={'s3_uri': s3_uri},
            UpdateExpression='SET sum_by_tspart = :val',
            ExpressionAttributeValues={':val': combined_summary}
        )

        return {
            'statusCode': 200,
            's3_uri': s3_uri,
            'body': json.dumps({'sum_by_tspart': combined_summary}, ensure_ascii=False)
        }

    except ClientError as err:
        message = err.response['Error']['Message']
        logger.error('A client error occurred: %s', message)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': message})
        }