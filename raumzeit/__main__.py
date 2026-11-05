"""Start: python -m raumzeit [--demo] [--port 5050]."""

import argparse
from pathlib import Path
from .web import create_app


def main():
    parser = argparse.ArgumentParser(description="Raumzeit lokal starten")
    parser.add_argument("--demo", action="store_true", help="Getrennte Datenbank mit Beispieldaten verwenden")
    parser.add_argument("--port", type=int, default=5050)
    parser.add_argument("--database", type=Path, help="Optionaler Pfad zur SQLite-Datenbank")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    database = args.database or root / "instance" / ("demo.sqlite3" if args.demo else "raumzeit.sqlite3")
    app = create_app({"DATABASE": str(database), "DEMO":args.demo})
    print(f"\nRaumzeit öffnen: http://127.0.0.1:{args.port}\nBeenden mit Strg+C.\n", flush=True)
    app.run(host="127.0.0.1", port=args.port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
