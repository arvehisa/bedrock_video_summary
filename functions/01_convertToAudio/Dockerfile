# AWS LambdaのPythonランタイムベースイメージを使用
FROM public.ecr.aws/lambda/python:3.12

# 必要なツールをインストール
RUN microdnf install -y tar gzip xz

# FFMPEGのバイナリをダウンロードして解凍
RUN curl -O https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    tar -xJf ffmpeg-release-amd64-static.tar.xz && \
    mv ffmpeg-*/ffmpeg /usr/local/bin/ && \
    mv ffmpeg-*/ffprobe /usr/local/bin/ && \
    rm -rf ffmpeg-*

# Lambda関数のコードをコピー
COPY main.py ./

# Lambda関数のハンドラーを指定
CMD ["main.lambda_handler"]