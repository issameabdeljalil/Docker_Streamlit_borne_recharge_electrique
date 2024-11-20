FROM python:3.11-slim

WORKDIR /app_api

COPY . .

RUN chmod +x install.sh && ./install.sh

CMD chmod +x bin/run.sh && ./bin/run.sh