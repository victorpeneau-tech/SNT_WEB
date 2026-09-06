from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3


ROOT = Path(__file__).parent
DATABASE = ROOT / "clicks.db"


def initialize_database():
    with sqlite3.connect(DATABASE) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS clicks (id INTEGER PRIMARY KEY CHECK (id = 1), count INTEGER NOT NULL DEFAULT 0)"
        )
        connection.execute("INSERT OR IGNORE INTO clicks (id, count) VALUES (1, 0)")


def get_count():
    with sqlite3.connect(DATABASE) as connection:
        return connection.execute("SELECT count FROM clicks WHERE id = 1").fetchone()[0]


def increment_count():
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("UPDATE clicks SET count = count + 1 WHERE id = 1")
        return connection.execute("SELECT count FROM clicks WHERE id = 1").fetchone()[0]


class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def send_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/count":
            self.send_json({"count": get_count()})
            return
        super().do_GET()

    def do_POST(self):
        if self.path == "/api/click":
            self.send_json({"count": increment_count()})
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Route introuvable")

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


if __name__ == "__main__":
    initialize_database()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), RequestHandler)
    print("Serveur disponible sur http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServeur arrêté.")
    finally:
        server.server_close()