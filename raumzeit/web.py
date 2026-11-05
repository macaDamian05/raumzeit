"""HTTP-Adapter und Zusammensetzen der Anwendung (Application Factory)."""

from pathlib import Path
import secrets
import sqlite3
from flask import Flask, jsonify, render_template, request, session
from werkzeug.exceptions import HTTPException
from . import __version__
from .application import PlannerService
from .domain import COLORS, EQUIPMENT, DomainError
from .storage import SQLiteFactory, initialize


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_path=str(Path(__file__).resolve().parents[1] / "instance"))
    app.config.from_mapping(
        DATABASE=str(Path(app.instance_path) / "raumzeit.sqlite3"), DEMO=False,
        MAX_CONTENT_LENGTH=65536, TRUSTED_HOSTS=["localhost", "127.0.0.1"],
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Strict",
    )
    if config:
        app.config.update(config)
    if not app.config.get("SECRET_KEY"):
        key_path = Path(app.config["DATABASE"]).with_suffix(".secret")
        key_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with key_path.open("x", encoding="ascii") as handle:
                handle.write(secrets.token_hex(32))
        except FileExistsError:
            pass
        app.config["SECRET_KEY"] = key_path.read_text(encoding="ascii")
    initialize(app.config["DATABASE"])
    service = PlannerService(SQLiteFactory(app.config["DATABASE"]))
    app.extensions["planner"] = service
    if app.config["DEMO"]:
        from .demo import seed_demo
        seed_demo(service)

    @app.before_request
    def protect_changes():
        if request.url_rule is not None and request.path.startswith("/api/") and request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            token = request.headers.get("X-CSRF-Token", "")
            expected = session.get("csrf", "")
            if (
                not token
                or not token.isascii()
                or not isinstance(expected, str)
                or not expected.isascii()
                or not secrets.compare_digest(token, expected)
            ):
                return jsonify(error="Die Sitzung ist abgelaufen. Bitte die Seite neu laden.", code="csrf"), 403

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'self'"
        response.headers["Cache-Control"] = "no-store"
        return response

    def body() -> dict:
        if not request.is_json:
            from werkzeug.exceptions import UnsupportedMediaType
            raise UnsupportedMediaType()
        data = request.get_json()
        if not isinstance(data, dict):
            raise DomainError("Die Anfrage muss ein JSON-Objekt enthalten.")
        return data

    @app.errorhandler(DomainError)
    def domain_error(error):
        status = {"not_found":404, "conflict":409, "stale":409}.get(error.code, 422)
        return jsonify(error=str(error), code=error.code, field=error.field), status

    @app.errorhandler(HTTPException)
    def http_error(error):
        messages = {400:"Die Anfrage ist ungültig.",404:"Die Adresse wurde nicht gefunden.",405:"Diese Aktion ist nicht verfügbar.",413:"Die Anfrage ist zu groß.",415:"Bitte Daten als JSON senden."}
        return jsonify(error=messages.get(error.code, "Die Anfrage konnte nicht verarbeitet werden."), code="http_error"), error.code

    @app.errorhandler(sqlite3.OperationalError)
    def database_error(error):
        app.logger.error("SQLite operation failed: %s", error)
        response = jsonify(error="Die Datenbank ist gerade nicht verfügbar. Bitte erneut versuchen.", code="database_busy")
        response.headers["Retry-After"] = "1"
        return response, 503

    @app.get("/")
    def index():
        session.setdefault("csrf", secrets.token_urlsafe(32))
        return render_template("index.html", csrf=session["csrf"], demo=app.config["DEMO"], version=__version__)

    @app.get("/api/config")
    def configuration():
        return jsonify(equipment=EQUIPMENT, colors=COLORS, demo=app.config["DEMO"], version=__version__, timezone="Europe/Berlin", opening_hours="Mo-Fr, 08:00-20:00", slot_minutes=15)

    @app.get("/api/rooms")
    def rooms():
        return jsonify(rooms=service.list_rooms())

    @app.post("/api/rooms")
    def create_room():
        return jsonify(room=service.save_room(body())), 201

    @app.put("/api/rooms/<room_id>")
    def update_room(room_id):
        return jsonify(room=service.save_room(body(), room_id))

    @app.get("/api/bookings")
    def bookings():
        return jsonify(bookings=service.list_bookings(request.args.get("from"), request.args.get("to"), request.args.get("room_id") or None))

    @app.post("/api/bookings")
    def create_booking():
        return jsonify(booking=service.save_booking(body())), 201

    @app.put("/api/bookings/<booking_id>")
    def update_booking(booking_id):
        return jsonify(booking=service.save_booking(body(), booking_id))

    @app.post("/api/bookings/<booking_id>/cancel")
    def cancel_booking(booking_id):
        return jsonify(booking=service.cancel_booking(booking_id, body()))

    return app
