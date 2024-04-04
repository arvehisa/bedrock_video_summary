import streamlit as st

# サイドバーにファイルアップロード機能を設置
with st.sidebar:
    uploaded_file = st.file_uploader("Choose a file")
    video_name = st.text_input("Video Name (YYYYMMDD_xx)")
    description = st.text_area("Description (optional)")
    url = st.text_input("URL (optional)")

    submit_button = st.button('Upload Video')

# アップロードされたビデオのリスト（ここでは仮のデータを使用）
videos = ["Video 1", "Video 2", "Video 3"]  # 実際にはDynamoDBから取得したデータを使用する

# サイドバーにビデオのリストを表示するセレクトボックスを設置
selected_video = st.sidebar.selectbox("Select a video", videos)

# 選択されたビデオに関する情報をメインエリアに表示
if selected_video:
    # ここでは仮のデータを表示しています。実際には選択されたビデオに対応する情報をDynamoDBから取得して表示します。
    st.write(f"### Video Title: {selected_video}")
    st.write("URL: URL goes here (if available)")  # URLがあれば表示
    st.write("### Summary")
    st.write("This is a summary of the video.")
    st.write("### Timestamp-wise Summary")
    st.write("- 00:00: Introduction")
    st.write("- 01:00: Main content starts")
    st.write("- 02:00: Conclusion")

if submit_button:
    # ここでファイルアップロードとDynamoDBへの情報保存の処理を行う
    # アップロードされたファイルと入力された情報を使用して処理を行う
    st.sidebar.write("Video uploaded successfully!")
