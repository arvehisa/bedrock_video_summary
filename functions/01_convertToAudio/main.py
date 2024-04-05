import os
import boto3
import subprocess
from urllib.parse import unquote_plus

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    key = unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    download_path = f'/tmp/{os.path.basename(key)}'
    output_path = f'/tmp/{os.path.splitext(os.path.basename(key))[0]}.m4a'

    output_bucket = 'videosum-audio-output'
    
    s3_client.download_file(source_bucket, key, download_path)
    
    convert_mp4_to_m4a(download_path, output_path)
    
    s3_client.upload_file(output_path, output_bucket, os.path.basename(output_path))


def convert_mp4_to_m4a(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, '-vn', '-acodec', 'copy', output_file]
    subprocess.run(command, check=True)