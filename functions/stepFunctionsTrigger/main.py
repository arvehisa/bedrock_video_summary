import json

def lambda_handler(event, context):
    print('hello')
    return {
        'statusCode': 200,
        'body': json.dumps("hello world")
    }