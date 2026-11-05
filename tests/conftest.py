from pathlib import Path
import pytest
from raumzeit.application import PlannerService
from raumzeit.storage import SQLiteFactory, initialize
from raumzeit.web import create_app


@pytest.fixture
def database(tmp_path: Path):
    path = tmp_path / "test.sqlite3"
    initialize(path)
    return path


@pytest.fixture
def service(database):
    return PlannerService(SQLiteFactory(database))


@pytest.fixture
def room(service):
    return service.save_room(dict(name="Horizont", capacity=12, location="1. OG", equipment=["Whiteboard"], color="blue"))


@pytest.fixture
def draft(room):
    return dict(room_id=room["id"], title="Projektbesprechung", organizer="Test Person", participants=6, start="2026-10-19T09:00", end="2026-10-19T10:00")


@pytest.fixture
def app(database):
    return create_app({"DATABASE":str(database),"TESTING":True,"SECRET_KEY":"test-key-only"})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def csrf(client):
    client.get("/")
    with client.session_transaction() as session:
        return {"X-CSRF-Token":session["csrf"]}
