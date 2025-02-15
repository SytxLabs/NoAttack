FROM python:3.12-alpine AS build

RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-alpine

WORKDIR /app

COPY --from=build /install /usr/local

COPY . .

RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev

CMD ["python3", "-u", "main.py"]
