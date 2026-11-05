import sqlite3
import pytest
from raumzeit.demo import seed_demo
from raumzeit.web import create_app


def create_room(client,csrf):
    response=client.post("/api/rooms",headers=csrf,json=dict(name="Raum A",capacity=10,location="EG",color="blue",equipment=[]))
    assert response.status_code == 201
    return response.json["room"]


def payload(room):
    return dict(room_id=room["id"],title="API Test",organizer="Test Person",participants=4,start="2026-10-19T09:00",end="2026-10-19T10:00")


def test_index_and_security_headers(client):
    response=client.get("/")
    assert response.status_code == 200
    assert b'lang="de"' in response.data
    assert b'name="csrf-token"' in response.data
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "script-src 'self'" in response.headers["Content-Security-Policy"]
    assert "HttpOnly" in response.headers["Set-Cookie"]
    assert "SameSite=Strict" in response.headers["Set-Cookie"]


def test_configuration_and_empty_state(client):
    assert client.get("/api/rooms").json == {"rooms":[]}
    assert client.get("/api/config").json["slot_minutes"] == 15
    assert client.get("/api/bookings?from=2026-10-19&to=2026-10-26").json == {"bookings":[]}


@pytest.mark.parametrize("method,path", [("post","/api/rooms"),("put","/api/rooms/x"),("post","/api/bookings"),("put","/api/bookings/x"),("post","/api/bookings/x/cancel")])
def test_mutations_require_csrf(client,method,path):
    assert getattr(client,method)(path,json={}).status_code == 403


def test_bad_csrf_rejected(client,csrf):
    assert client.post("/api/rooms",json={},headers={"X-CSRF-Token":"wrong"}).status_code == 403


def test_full_http_booking_flow(client,csrf):
    room=create_room(client,csrf)
    response=client.post("/api/bookings",headers=csrf,json=payload(room))
    assert response.status_code == 201
    booking=response.json["booking"]
    assert client.post("/api/bookings",headers=csrf,json=payload(room)).status_code == 409
    updated=client.put(f'/api/bookings/{booking["id"]}',headers=csrf,json=payload(room) | {"version":1,"title":"Neu"})
    assert updated.status_code == 200 and updated.json["booking"]["version"] == 2
    stale=client.put(f'/api/bookings/{booking["id"]}',headers=csrf,json=payload(room) | {"version":1})
    assert stale.status_code == 409 and stale.json["code"] == "stale"
    cancelled=client.post(f'/api/bookings/{booking["id"]}/cancel',headers=csrf,json={"version":2})
    assert cancelled.status_code == 200 and cancelled.json["booking"]["status"] == "cancelled"
    assert client.post("/api/bookings",headers=csrf,json=payload(room)).status_code == 201
    all_bookings=client.get(f'/api/bookings?from=2026-10-19&to=2026-10-26&room_id={room["id"]}').json["bookings"]
    assert len(all_bookings) == 2


def test_room_edit_http(client,csrf):
    room=create_room(client,csrf)
    response=client.put(f'/api/rooms/{room["id"]}',headers=csrf,json=room | {"capacity":20})
    assert response.status_code == 200 and response.json["room"]["capacity"] == 20


def test_validation_and_unknown_record_statuses(client,csrf):
    assert client.post("/api/rooms",headers=csrf,json={}).status_code == 422
    room=create_room(client,csrf)
    response=client.post("/api/bookings",headers=csrf,json=payload(room) | {"participants":11})
    assert response.status_code == 422 and response.json["field"] == "participants"
    assert client.post("/api/bookings/missing/cancel",headers=csrf,json={"version":1}).status_code == 404
    assert client.get("/api/bookings").status_code == 422


def test_json_only_and_malformed_bodies(client,csrf):
    assert client.post("/api/rooms",headers=csrf,data="name=x").status_code == 415
    assert client.post("/api/rooms",headers=csrf,json=[]).status_code == 422
    assert client.post("/api/rooms",headers=csrf,data="{",content_type="application/json").status_code == 400
    assert client.post("/api/rooms",headers=csrf,json={"data":"x"*70000}).status_code == 413


def test_unknown_route_and_method(client):
    assert client.get("/api/missing").status_code == 404
    assert client.delete("/api/config").status_code == 405


def test_untrusted_host_blocked(client):
    assert client.get("/",headers={"Host":"attacker.example"}).status_code == 400


def test_database_error_is_safe_and_retryable(client,app,monkeypatch):
    def fail(): raise sqlite3.OperationalError("private database path")
    monkeypatch.setattr(app.extensions["planner"],"list_rooms",fail)
    response=client.get("/api/rooms")
    assert response.status_code == 503 and response.headers["Retry-After"] == "1"
    assert "private" not in response.get_data(as_text=True)


def test_sql_parameterization_preserves_literal_data(client,csrf):
    room=create_room(client,csrf)
    title="'); DROP TABLE rooms; -- <script>alert(1)</script>"
    assert client.post("/api/bookings",headers=csrf,json=payload(room) | {"title":title}).status_code == 201
    assert client.get("/api/rooms").json["rooms"][0]["name"] == "Raum A"
    assert client.get("/api/bookings?from=2026-10-19&to=2026-10-26").json["bookings"][0]["title"] == title


def test_demo_is_separate_and_idempotent(tmp_path):
    demo=create_app({"DATABASE":str(tmp_path/"demo.db"),"DEMO":True,"TESTING":True,"SECRET_KEY":"test"})
    service=demo.extensions["planner"]
    assert len(service.list_rooms()) == 4
    seed_demo(service)
    assert len(service.list_rooms()) == 4
    empty=create_app({"DATABASE":str(tmp_path/"empty.db"),"TESTING":True,"SECRET_KEY":"test"})
    assert not empty.extensions["planner"].list_rooms()


def test_secret_key_survives_restart(tmp_path):
    config={"DATABASE":str(tmp_path/"restart.db"),"TESTING":True}
    first=create_app(config)
    second=create_app(config)
    assert first.config["SECRET_KEY"] == second.config["SECRET_KEY"]


@pytest.mark.parametrize("asset", ["app.css","app.js","favicon.svg"])
def test_assets_served_locally(client,asset):
    assert client.get(f"/static/{asset}").status_code == 200
