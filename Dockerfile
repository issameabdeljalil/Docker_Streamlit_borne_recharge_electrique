FROM python:3.11

WORKDIR /app_api

COPY . .

RUN chmod +x install.sh && ./install.sh
RUN chmod +x bin/run.sh && ./bin/run.sh

CMD ["echo", "Lancement de l'application"]