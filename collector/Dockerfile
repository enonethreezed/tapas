FROM alpine:3.21

RUN apk add --no-cache python3 py3-psycopg2

WORKDIR /app
COPY collector.py /app/collector.py

EXPOSE 1514/tcp

CMD ["python3", "/app/collector.py"]
