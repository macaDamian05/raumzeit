"""Isolierter Testserver. Keine zusätzlichen Routen oder Produktionsoptionen."""

from pathlib import Path
import logging
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from raumzeit.web import create_app

if __name__ == "__main__":
    app = create_app({"DATABASE": sys.argv[1], "SECRET_KEY": "browser-tests-only"})
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    app.run(host="127.0.0.1", port=5051, debug=False, threaded=True)
