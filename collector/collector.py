import os
import socket
import time

import psycopg2


def connect_db():
    while True:
        try:
            return psycopg2.connect(
                host="db",
                dbname=os.environ["POSTGRES_DB"],
                user=os.environ["POSTGRES_USER"],
                password=os.environ["POSTGRES_PASSWORD"],
            )
        except psycopg2.OperationalError:
            time.sleep(2)


db = connect_db()
with db, db.cursor() as cursor:
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS syslog_events ("
        "id BIGSERIAL PRIMARY KEY, received_at TIMESTAMPTZ NOT NULL DEFAULT now(), "
        "source_ip INET NOT NULL, message TEXT NOT NULL)"
    )

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 1514))
    server.listen()
    while True:
        connection, address = server.accept()
        with connection:
            buffer = b""
            while chunk := connection.recv(4096):
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if line:
                        with db, db.cursor() as cursor:
                            cursor.execute(
                                "INSERT INTO syslog_events (source_ip, message) VALUES (%s, %s)",
                                (address[0], line.decode("utf-8", errors="replace")),
                            )
