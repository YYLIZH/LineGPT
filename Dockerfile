FROM python:3.9
COPY requirements.txt /
COPY .env /.env

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1

RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get update \
    && apt-get install -y \
    && mkdir /work
COPY ./api /work/api
WORKDIR /work
