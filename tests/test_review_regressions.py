"""Regressionen aus der am 29.10.2026 übermittelten unabhängigen Bewertung."""

import pytest


def test_non_ascii_csrf_is_forbidden(client, csrf):
    response = client.post(
        "/api/rooms", headers={"X-CSRF-Token": "ä"}, json={}
    )
    assert response.status_code == 403
    assert response.json["code"] == "csrf"


def test_stale_room_edit_http_preserves_current_record(client, csrf, room):
    path = f'/api/rooms/{room["id"]}'
    current = client.put(
        path, headers=csrf, json=room | {"name": "Aktueller Raum", "version": 1}
    )
    assert current.status_code == 200

    stale = client.put(
        path, headers=csrf, json=room | {"name": "Veralteter Dialog", "version": 1}
    )
    assert stale.status_code == 409
    assert stale.json["code"] == "stale"
    rooms = client.get("/api/rooms").json["rooms"]
    assert rooms == [current.json["room"]]


@pytest.mark.parametrize("token", ["ä", "a" * 42 + "ä", "💡"])
@pytest.mark.parametrize("method,path", [
    ("post", "/api/rooms"), ("put", "/api/rooms/missing"),
    ("post", "/api/bookings"), ("put", "/api/bookings/missing"),
    ("post", "/api/bookings/missing/cancel"),
])
def test_unicode_csrf_rejected_on_every_mutation(client, csrf, token, method, path):
    response = getattr(client, method)(path, headers={"X-CSRF-Token": token}, json={})
    assert response.status_code == 403 and response.json["code"] == "csrf"


def test_valid_csrf_still_allows_creation(client, csrf):
    response = client.post("/api/rooms", headers=csrf, json={
        "name": "Gültig", "capacity": 4, "location": "EG"
    })
    assert response.status_code == 201
    assert response.json["room"]["version"] == 1
