from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Barrier
import sqlite3

import pytest

from raumzeit.application import PlannerService
from raumzeit.domain import DomainError
from raumzeit.storage import SQLiteFactory, initialize


def test_room_version_increments_and_survives_restart(service, room, database):
    assert room["version"] == 1
    updated = service.save_room(room | {"location": "Zweiter Standort"}, room["id"])
    assert updated["version"] == 2
    restarted = PlannerService(SQLiteFactory(database))
    assert restarted.list_rooms() == [updated]


@pytest.mark.parametrize("version", [None, 0, -1, True, "1"])
def test_room_edit_requires_positive_integer_version(service, room, version):
    with pytest.raises(DomainError) as caught:
        service.save_room(room | {"version": version}, room["id"])
    assert caught.value.code == "validation"
    assert service.list_rooms() == [room]


def test_room_edit_missing_version_rejected(service, room):
    data = {key: value for key, value in room.items() if key != "version"}
    with pytest.raises(DomainError):
        service.save_room(data, room["id"])
    assert service.list_rooms() == [room]


def test_failed_room_edit_does_not_consume_version(service, room, draft):
    service.save_booking(draft)
    with pytest.raises(DomainError):
        service.save_room(room | {"capacity": 5}, room["id"])
    assert service.list_rooms() == [room]
    updated = service.save_room(room | {"capacity": 6}, room["id"])
    assert updated["version"] == 2


def test_concurrent_room_edits_only_one_succeeds(service, room, database):
    barrier = Barrier(2)

    def change(name):
        own_service = PlannerService(SQLiteFactory(database))
        barrier.wait(timeout=5)
        try:
            return own_service.save_room(room | {"name": name}, room["id"])
        except DomainError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(change, ["Änderung A", "Änderung B"]))
    successes = [item for item in results if isinstance(item, dict)]
    assert len(successes) == 1 and results.count("stale") == 1
    assert service.list_rooms() == successes
    assert successes[0]["version"] == 2


def test_repository_compare_and_swap_rejects_old_room(database, service, room):
    factory = SQLiteFactory(database)
    with factory(write=True) as uow:
        original = uow.rooms.get(room["id"])
        uow.rooms.save(replace(original, name="Aktuell", version=2), updating=True)
    with pytest.raises(DomainError) as caught:
        with factory(write=True) as uow:
            uow.rooms.save(replace(original, name="Veraltet", version=2), updating=True)
    assert caught.value.code == "stale"
    assert service.list_rooms()[0]["name"] == "Aktuell"


@pytest.fixture
def legacy_database(tmp_path):
    """Unabhängig festgehaltenes Schema v1, nicht aus dem neuen Schema abgeleitet."""
    path = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.executescript("""
            CREATE TABLE rooms (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, name_key TEXT NOT NULL UNIQUE,
                capacity INTEGER NOT NULL CHECK(capacity BETWEEN 1 AND 500),
                location TEXT NOT NULL, equipment TEXT NOT NULL, color TEXT NOT NULL
            );
            CREATE TABLE bookings (
                id TEXT PRIMARY KEY, room_id TEXT NOT NULL REFERENCES rooms(id),
                title TEXT NOT NULL, organizer TEXT NOT NULL,
                participants INTEGER NOT NULL CHECK(participants BETWEEN 1 AND 500),
                start TEXT NOT NULL, end TEXT NOT NULL CHECK(end > start),
                status TEXT NOT NULL CHECK(status IN ('active','cancelled')),
                version INTEGER NOT NULL CHECK(version >= 1)
            );
            INSERT INTO rooms VALUES ('r1','Altbestand','altbestand',8,'EG','[]','blue');
            INSERT INTO bookings VALUES (
                'b1','r1','Erhalten','Test Person',4,
                '2026-10-26T09:00','2026-10-26T10:00','active',3
            );
            PRAGMA user_version = 1;
        """)
    return path


def test_legacy_migration_preserves_data_and_is_idempotent(legacy_database):
    initialize(legacy_database)
    service = PlannerService(SQLiteFactory(legacy_database))
    room = service.list_rooms()[0]
    assert room["version"] == 1 and room["name"] == "Altbestand"
    bookings = service.list_bookings("2026-10-26", "2026-10-27")
    assert len(bookings) == 1 and bookings[0]["version"] == 3
    updated = service.save_room(room | {"location": "OG"}, room["id"])
    initialize(legacy_database)
    assert service.list_rooms() == [updated] and updated["version"] == 2
    assert service.list_bookings("2026-10-26", "2026-10-27") == bookings
    with sqlite3.connect(legacy_database) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 2
        assert not connection.execute("PRAGMA foreign_key_check").fetchall()


def test_newer_schema_not_downgraded(legacy_database):
    with sqlite3.connect(legacy_database) as connection:
        connection.execute("PRAGMA user_version = 3")
    with pytest.raises(sqlite3.DatabaseError, match="neueren"):
        initialize(legacy_database)
    with sqlite3.connect(legacy_database) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 3
        assert "version" not in {row[1] for row in connection.execute("PRAGMA table_info(rooms)")}
        assert connection.execute("SELECT COUNT(*) FROM bookings").fetchone()[0] == 1
