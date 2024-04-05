import boto3
import json
import urllib.request

def lambda_handler(event, context):
    # Initialize AWS clients
    transcribe_client = boto3.client('transcribe')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('videosum-table') 

    # Extract jobName and s3_uri from the event
    job_name = event['Payload'].get('jobName')
    s3_uri = event['Payload']['s3_uri']

    # Check Transcribe job status
    response = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
    job_status = response['TranscriptionJob']['TranscriptionJobStatus']

    if job_status == 'COMPLETED':
        # Get the transcription result
        transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']

        # Fetch and load transcript data from the URI
        with urllib.request.urlopen(transcript_uri) as url:
            transcript_data = json.loads(url.read().decode())

        # Format transcript data
        formatted_transcript = format_transcript(transcript_data)

        # Insert data into DynamoDB
        response = table.put_item(
           Item={
                's3_uri': s3_uri,
                'transcript_formatted': formatted_transcript,
            }
        )

        return {
            'statusCode': 200,
            's3_uri' : s3_uri,
            'jobName': job_name,
            'jobStatus': job_status
        }
    else:
        return {
            'statusCode': 202,
            'jobName': job_name,
            'jobStatus': job_status
        }

def format_transcript(data):
    results = []
    current_speaker = None
    current_segment = []

    for item in data['results']['items']:
        if 'speaker_label' in item:
            if current_speaker != item['speaker_label'] or item['type'] == 'punctuation':
                if current_segment:
                    results.append(f"{current_speaker}, {round(float(current_segment[0]['start_time']), 1)}, {''.join([seg['content'] for seg in current_segment])}")
                    current_segment = []
                current_speaker = item['speaker_label']

        if item['type'] == 'pronunciation':
            current_segment.append({
                'start_time': item['start_time'],
                'content': item['alternatives'][0]['content']
            })

    if current_segment:
        results.append(f"{current_speaker}, {round(float(current_segment[0]['start_time']), 1)}, {''.join([seg['content'] for seg in current_segment])}")

    return '\n'.join(results)