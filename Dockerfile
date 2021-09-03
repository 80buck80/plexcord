# syntax=docker/dockerfile:1

FROM amd64/python:3.6-alpine3.13

WORKDIR /plexcord

COPY requirements.txt requirements.txt

RUN apk add libffi-dev

RUN apk add build-base

RUN apk add ffmpeg

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3","bot.py"]
