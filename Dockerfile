FROM ubuntu:20.04
MAINTAINER JSK <powersung0511@gmail.com>

WORKDIR /app
RUN pip install poetry
RUN poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml /app/
RUN pip install --upgrade pip
RUN apt-get update

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul

RUN apt-get install -y tzdata

COPY * /app/
EXPOSE 80

