import streamlit as st
import boto3
from datetime import datetime

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = 'videosum-table'
table = dynamodb.Table(table_name)
s3 = boto3.client('s3')

# サイドバーにファイルアップロード機能を設置
with st.sidebar:
    uploaded_file = st.file_uploader("Choose a file")
    description = st.text_area("Description (optional)")
    url = st.text_input("URL (optional)")

    submit_button = st.button('Upload Video')

# アップロードされたビデオのリスト（DynamoDBから取得）
response = table.scan()
videos = [item['s3_uri'] for item in response['Items']]

# サイドバーにビデオのリストを表示するセレクトボックスを設置
selected_video = st.sidebar.selectbox("Select a video", videos)

# 選択されたビデオに関する情報をメインエリアに表示
if selected_video:
    # 選択されたビデオの情報をDynamoDBから取得
    response = table.get_item(Key={'s3_uri': f"s3://videosum-audio-output/{selected_video}"})
    print (selected_video)
    print(response)
    
    if 'Item' in response:
        item = response['Item']
        st.write(f"### Video Title: {item['video_name']}")
        st.write(f"URL: {item.get('video_url', 'URL not available')}")  # URLがあれば表示
        st.write("### Summary")
        st.write(item.get('sum_en', 'Summary not available'))
        st.write("### 日本語の要約")
        st.write(item.get('sum_ja', '日本語の要約はありません'))
        st.write("### Timestamp-wise Summary")
        st.write(item.get('sum_by_tspart', 'Timestamp-wise summary not available'))
    else:
        st.write("not in DB")

if submit_button:
    # ファイルアップロードとDynamoDBへの情報保存の処理を行う
    if uploaded_file:
        # アップロードされたファイルをS3に保存
        video_name = uploaded_file.name
        s3_uri = f"s3://videosum-video-input/{video_name}"
        s3.upload_fileobj(uploaded_file, "videosum-video-input", video_name)
        upload_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # DynamoDBにビデオの情報を保存
        item = {
            's3_uri': s3_uri,
            'video_name': video_name,
            'video_url': url,
            'video_description': description,
            'upload_ts': upload_ts
        }
        table.put_item(Item=item)
        
        st.sidebar.write("Video uploaded successfully!")
    else:
        st.sidebar.write("Please provide a file.")