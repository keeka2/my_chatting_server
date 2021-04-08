FROM python:3.7
MAINTAINER JSK <powersung0511@gmail.com>
RUN apt-get update

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false

WORKDIR /app
COPY poetry.lock pyproject.toml /app/
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul
RUN poetry install -n
RUN apt-get install -y tzdata

COPY * /app/
EXPOSE 80

