FROM python:3
RUN apt-get update && apt-get install -y ffmpeg
ENV PYTHONBUFFERED=1
COPY ./requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /code
