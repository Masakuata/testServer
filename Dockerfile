FROM python:3.9.5-alpine3.12

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip

RUN apk update && apk add python3-dev gcc libc-dev

RUN pip --no-cache-dir install -r requirements.txt

RUN pip install gunicorn

CMD ["gunicorn", "-b", "0.0.0.0:42101", "main:app"]