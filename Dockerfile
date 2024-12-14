FROM python:3.11-slim

WORKDIR /app_api

COPY . .

RUN apt-get update && apt-get install -y curl
RUN chmod +x install.sh && ./install.sh

CMD chmod +x bin/run.sh && ./bin/run.sh