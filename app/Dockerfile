FROM python:3.12
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 80
ENTRYPOINT ["streamlit", "run", "--server.port", "80"]
CMD ["main.py"]