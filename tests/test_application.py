from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import pytest
from raumzeit.application import PlannerService
from raumzeit.domain import DomainError
from raumzeit.storage import SQLiteFactory


def week(service):
    return service.list_bookings("2026-10-19","2026-10-26")


def test_create_and_persist(service, database, draft):
    saved = service.save_booking(draft)
    restarted = PlannerService(SQLiteFactory(database))
    assert week(restarted) == [saved]
    assert saved["version"] == 1


@pytest.mark.parametrize("start,end", [("09:00","10:00"),("08:30","09:15"),("09:45","10:15"),("09:15","09:45"),("08:00","11:00")])
def test_overlap_rejected_without_partial_write(service, draft, start, end):
    original = service.save_booking(draft)
    with pytest.raises(DomainError, match="bereits gebucht"):
        service.save_booking(draft | {"start":f"2026-10-19T{start}","end":f"2026-10-19T{end}"})
    assert week(service) == [original]


@pytest.mark.parametrize("start,end", [("08:00","09:00"),("10:00","11:00")])
def test_adjacent_bookings_allowed(service, draft, start,end):
    service.save_booking(draft)
    service.save_booking(draft | {"start":f"2026-10-19T{start}","end":f"2026-10-19T{end}"})
    assert len(week(service)) == 2


def test_same_time_other_room_allowed(service, draft):
    other = service.save_room(dict(name="Atelier",capacity=8,location="EG"))
    service.save_booking(draft)
    service.save_booking(draft | {"room_id":other["id"]})
    assert len(week(service)) == 2


def test_capacity_exactly_allowed_and_excess_rejected(service,draft):
    saved = service.save_booking(draft | {"participants":12})
    with pytest.raises(DomainError,match="höchstens 12"):
        service.save_booking(draft | {"start":"2026-10-19T10:00","end":"2026-10-19T11:00","participants":13})
    assert week(service) == [saved]


def test_edit_excludes_itself_and_increments_version(service,draft):
    saved = service.save_booking(draft)
    updated = service.save_booking(draft | {"title":"Geändert","version":1},saved["id"])
    assert updated["version"] == 2
    assert updated["title"] == "Geändert"
    assert len(week(service)) == 1


def test_edit_conflict_rolls_back(service,draft):
    first = service.save_booking(draft)
    service.save_booking(draft | {"start":"2026-10-19T10:00","end":"2026-10-19T11:00"})
    with pytest.raises(DomainError):
        service.save_booking(draft | {"end":"2026-10-19T10:15","version":1},first["id"])
    assert next(b for b in week(service) if b["id"] == first["id"]) == first


def test_stale_update_cannot_overwrite(service,draft):
    saved = service.save_booking(draft)
    updated = service.save_booking(draft | {"version":1,"title":"Aktuell"},saved["id"])
    with pytest.raises(DomainError,match="zwischenzeitlich"):
        service.save_booking(draft | {"version":1},saved["id"])
    assert week(service) == [updated]


def test_cancel_frees_slot_and_retains_history(service,draft):
    saved = service.save_booking(draft)
    cancelled = service.cancel_booking(saved["id"],{"version":1})
    assert cancelled["status"] == "cancelled" and cancelled["version"] == 2
    replacement = service.save_booking(draft)
    assert {b["id"] for b in week(service)} == {saved["id"],replacement["id"]}
    assert service.cancel_booking(saved["id"],{"version":2}) == cancelled
    with pytest.raises(DomainError,match="stornierte"):
        service.save_booking(draft | {"version":2},saved["id"])


def test_stale_cancel_rejected(service,draft):
    saved=service.save_booking(draft)
    service.save_booking(draft | {"version":1},saved["id"])
    with pytest.raises(DomainError,match="zwischenzeitlich"):
        service.cancel_booking(saved["id"],{"version":1})


def test_duplicate_room_name_unicode_casefold(service):
    service.save_room(dict(name="Straße",capacity=4,location="EG"))
    with pytest.raises(DomainError,match="existiert"):
        service.save_room(dict(name="STRASSE",capacity=4,location="EG"))


def test_room_edit_protects_booked_capacity(service,room,draft):
    service.save_booking(draft)
    with pytest.raises(DomainError,match="mehr Plätze"):
        service.save_room(room | {"capacity":5},room["id"])
    assert service.list_rooms()[0]["capacity"] == 12
    updated = service.save_room(room | {"name":"Neu","capacity":6},room["id"])
    assert updated["name"] == "Neu"


def test_room_can_shrink_after_cancellation(service,room,draft):
    saved=service.save_booking(draft)
    service.cancel_booking(saved["id"],{"version":1})
    assert service.save_room(room | {"capacity":1},room["id"])["capacity"] == 1


@pytest.mark.parametrize("first,last", [(None,None),("invalid","2026-10-26"),("2026-10-19","2026-10-19"),("2026-10-26","2026-10-19"),("2026-10-19","2026-12-01")])
def test_invalid_query_range(service,first,last):
    with pytest.raises(DomainError):
        service.list_bookings(first,last)


def test_range_is_end_exclusive_and_room_filter_works(service,draft,room):
    service.save_booking(draft)
    assert len(service.list_bookings("2026-10-19","2026-10-20",room["id"])) == 1
    assert not service.list_bookings("2026-10-20","2026-10-21")


@pytest.mark.parametrize("action", ["book_room","update_room","update_booking","cancel_booking","filter_room"])
def test_missing_entity(service,draft,room,action):
    with pytest.raises(DomainError) as caught:
        if action == "book_room": service.save_booking(draft | {"room_id":"missing"})
        elif action == "update_room": service.save_room(room,"missing")
        elif action == "update_booking": service.save_booking(draft | {"version":1},"missing")
        elif action == "cancel_booking": service.cancel_booking("missing",{"version":1})
        else: service.list_bookings("2026-10-19","2026-10-26","missing")
    assert caught.value.code == "not_found"


def test_concurrent_requests_only_one_succeeds(service,database,draft):
    """Zwei unabhängige Verbindungen konkurrieren um denselben Zeitraum."""
    barrier = Barrier(2)
    def request():
        own_service=PlannerService(SQLiteFactory(database))
        barrier.wait(timeout=5)
        try:
            own_service.save_booking(draft)
            return "created"
        except DomainError as error:
            return error.code
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes=list(pool.map(lambda _:request(),range(2)))
    assert sorted(outcomes) == ["conflict","created"]
    assert len(week(service)) == 1
