FROM python:rc-alpine3.13

WORKDIR /plexcord

COPY requirements.txt requirements.txt

RUN apk add libffi-dev

RUN apk add build-base

RUN apk add ffmpeg

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "bot.py"]
