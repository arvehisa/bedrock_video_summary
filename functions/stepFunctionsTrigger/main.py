import json
import boto3

def lambda_handler(event, context):
    # S3バケットとオブジェクト情報を取得
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    # Step Functionsクライアントを作成
    sf_client = boto3.client('stepfunctions')
    
    # Step Functionsの状態マシンARNを指定
    state_machine_arn = 'arn:aws:states:us-east-1:618044871166:stateMachine:videosum-sfn'
    
    # 入力データを作成
    input_data = {
        's3Bucket': bucket_name,
        's3Key': object_key
    }
    
    # Step Functionsの実行を開始
    response = sf_client.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps(input_data)
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Step Functions execution started!')
    }