"""SQLite-Adapter. BEGIN IMMEDIATE serialisiert konkurrierende Änderungen."""

from contextlib import AbstractContextManager
from pathlib import Path
import json
import sqlite3
from .domain import Booking, DomainError, Room

SCHEMA = """
CREATE TABLE IF NOT EXISTS rooms (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, name_key TEXT NOT NULL UNIQUE,
 capacity INTEGER NOT NULL CHECK(capacity BETWEEN 1 AND 500), location TEXT NOT NULL,
 equipment TEXT NOT NULL, color TEXT NOT NULL,
 version INTEGER NOT NULL DEFAULT 1 CHECK(version >= 1)
);
CREATE TABLE IF NOT EXISTS bookings (
 id TEXT PRIMARY KEY, room_id TEXT NOT NULL REFERENCES rooms(id),
 title TEXT NOT NULL, organizer TEXT NOT NULL,
 participants INTEGER NOT NULL CHECK(participants BETWEEN 1 AND 500),
 start TEXT NOT NULL, end TEXT NOT NULL CHECK(end > start),
 status TEXT NOT NULL CHECK(status IN ('active','cancelled')),
 version INTEGER NOT NULL CHECK(version >= 1)
);
CREATE INDEX IF NOT EXISTS ix_booking_room_time ON bookings(room_id, status, start, end);
CREATE INDEX IF NOT EXISTS ix_booking_week ON bookings(start);
"""


def connect(path: Path | str) -> sqlite3.Connection:
    connection = sqlite3.connect(path, timeout=5, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize(path: Path | str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    connection = connect(path)
    try:
        # BEGIN inside executescript keeps DDL and migration in one transaction.
        connection.executescript("BEGIN IMMEDIATE;\n" + SCHEMA)
        current_version = connection.execute("PRAGMA user_version").fetchone()[0]
        if current_version > 2:
            raise sqlite3.DatabaseError("Die Datenbank stammt aus einer neueren Anwendungsversion.")
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(rooms)")}
        if "version" not in columns:
            connection.execute(
                "ALTER TABLE rooms ADD COLUMN version INTEGER NOT NULL DEFAULT 1 CHECK(version >= 1)"
            )
        connection.execute("PRAGMA user_version = 2")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


class SQLiteRooms:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    @staticmethod
    def _room(row: sqlite3.Row) -> Room:
        return Room(row["id"], row["name"], row["capacity"], row["location"], tuple(json.loads(row["equipment"])), row["color"], version=row["version"])

    def list(self) -> list[Room]:
        return [self._room(row) for row in self.connection.execute("SELECT * FROM rooms ORDER BY name_key")]

    def get(self, room_id: str) -> Room:
        row = self.connection.execute("SELECT * FROM rooms WHERE id = ?", (room_id,)).fetchone()
        if row is None:
            raise DomainError("Der Raum wurde nicht gefunden.", "not_found")
        return self._room(row)

    def save(self, room: Room, *, updating: bool) -> None:
        values = (room.name, room.name.casefold(), room.capacity, room.location, json.dumps(room.equipment), room.color, room.version, room.id)
        try:
            if updating:
                result = self.connection.execute(
                    "UPDATE rooms SET name=?,name_key=?,capacity=?,location=?,equipment=?,color=?,version=? WHERE id=? AND version=?",
                    values + (room.version - 1,),
                )
                if result.rowcount != 1:
                    raise DomainError("Der Raum wurde zwischenzeitlich geändert. Bitte die Seite neu laden.", "stale")
            else:
                self.connection.execute("INSERT INTO rooms(name,name_key,capacity,location,equipment,color,version,id) VALUES(?,?,?,?,?,?,?,?)", values)
        except sqlite3.IntegrityError as exc:
            raise DomainError("Ein Raum mit diesem Namen existiert bereits.", "conflict", "name") from exc


class SQLiteBookings:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def get(self, booking_id: str) -> Booking:
        row = self.connection.execute("SELECT * FROM bookings WHERE id=?", (booking_id,)).fetchone()
        if row is None:
            raise DomainError("Die Buchung wurde nicht gefunden.", "not_found")
        return Booking(**dict(row))

    def list_between(self, start: str, end: str, room_id: str | None = None) -> list[Booking]:
        sql = "SELECT * FROM bookings WHERE start < ? AND end > ?"
        values: list = [end, start]
        if room_id:
            sql += " AND room_id=?"
            values.append(room_id)
        return [Booking(**dict(row)) for row in self.connection.execute(sql + " ORDER BY start,id", values)]

    def conflict(self, room_id: str, start: str, end: str, excluding: str | None = None) -> Booking | None:
        # Halboffene Intervalle: [09:00,10:00) und [10:00,11:00) sind zulässig.
        row = self.connection.execute(
            "SELECT * FROM bookings WHERE room_id=? AND status='active' AND start < ? AND end > ? AND id != ? ORDER BY start LIMIT 1",
            (room_id, end, start, excluding or ""),
        ).fetchone()
        return Booking(**dict(row)) if row else None

    def largest_group(self, room_id: str) -> int:
        return self.connection.execute("SELECT COALESCE(MAX(participants),0) FROM bookings WHERE room_id=? AND status='active'", (room_id,)).fetchone()[0]

    def save(self, booking: Booking, *, updating: bool) -> None:
        values = (booking.room_id, booking.title, booking.organizer, booking.participants, booking.start, booking.end, booking.status, booking.version, booking.id)
        if updating:
            self.connection.execute("UPDATE bookings SET room_id=?,title=?,organizer=?,participants=?,start=?,end=?,status=?,version=? WHERE id=?", values)
        else:
            self.connection.execute("INSERT INTO bookings(room_id,title,organizer,participants,start,end,status,version,id) VALUES(?,?,?,?,?,?,?,?,?)", values)


class SQLiteUnitOfWork(AbstractContextManager):
    def __init__(self, path: Path | str, *, write: bool = False):
        self.path, self.write = path, write

    def __enter__(self):
        self.connection = connect(self.path)
        try:
            self.connection.execute("BEGIN IMMEDIATE" if self.write else "BEGIN")
        except Exception:
            self.connection.close()
            raise
        self.rooms = SQLiteRooms(self.connection)
        self.bookings = SQLiteBookings(self.connection)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.connection.execute("ROLLBACK" if exc_type else "COMMIT")
        finally:
            self.connection.close()


class SQLiteFactory:
    def __init__(self, path: Path | str):
        self.path = path

    def __call__(self, *, write: bool = False) -> SQLiteUnitOfWork:
        return SQLiteUnitOfWork(self.path, write=write)
