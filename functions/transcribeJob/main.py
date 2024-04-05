import boto3
import time
import os

def lambda_handler(event, context):
    # AWS Transcribeを使用するためのクライアントを作成
    transcribe_client = boto3.client('transcribe')
    
    # S3バケットとオブジェクト情報を取得
    s3_bucket_name = event['s3Bucket']
    s3_object_name = event['s3Key']
    
    # ジョブ名を一意にするため現在時刻を使用
    job_name = "TranscribeJob-" + str(int(time.time()))
    s3_uri = f's3://{s3_bucket_name}/{s3_object_name}'

    # Transcribeジョブを開始
    response = transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': s3_uri},
        MediaFormat=os.path.splitext(s3_object_name)[1][1:],  # ファイル拡張子からMediaFormatを取得
        LanguageCode='ja-JP',
        Settings={
            'ShowSpeakerLabels': True,
            'MaxSpeakerLabels': 10,
        }
    )
    
    # ジョブ名を返す
    return {
        'jobName': job_name,
        's3_uri': s3_uri
    }