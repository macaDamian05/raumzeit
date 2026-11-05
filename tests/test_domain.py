import pytest
from raumzeit.domain import BookingDraft, DomainError, Room

BASE = dict(room_id="room-1",title="Besprechung",organizer="Test Person",participants=2,start="2026-10-19T09:00",end="2026-10-19T10:00")


@pytest.mark.parametrize("changes", [
    {"title":""}, {"title":"   "}, {"title":"x"*121}, {"title":None},
    {"organizer":""}, {"organizer":"x"*101}, {"room_id":""},
    {"participants":0}, {"participants":-1}, {"participants":1.5}, {"participants":True}, {"participants":"2"}, {"participants":501},
    {"start":"2026-10-19"}, {"start":"2026-13-19T09:00"}, {"start":"2026-10-19T09:00Z"}, {"start":None},
    {"start":"2026-10-19T09:05"}, {"start":"2026-10-19T10:00"}, {"start":"2026-10-19T11:00"},
    {"end":"2026-10-20T10:00"}, {"start":"2026-10-24T09:00","end":"2026-10-24T10:00"},
    {"start":"2026-10-19T07:45"}, {"end":"2026-10-19T20:15"},
])
def test_invalid_booking_rejected(changes):
    """NF-02 / F03: Jede ungültige Eingabeklasse wird zurückgewiesen."""
    with pytest.raises(DomainError):
        BookingDraft.from_input(BASE | changes)


@pytest.mark.parametrize("start,end", [("08:00","08:15"),("19:45","20:00"),("08:00","20:00")])
def test_opening_boundaries_allowed(start,end):
    draft = BookingDraft.from_input(BASE | {"start":f"2026-10-19T{start}","end":f"2026-10-19T{end}"})
    assert draft.start.endswith(start)


def test_text_is_normalized():
    draft = BookingDraft.from_input(BASE | {"title":"  Projekt   Planung  "})
    assert draft.title == "Projekt Planung"


@pytest.mark.parametrize("changes", [{"capacity":0},{"capacity":True},{"name":""},{"location":""},{"equipment":["Unbekannt"]},{"equipment":"Beamer"},{"equipment":[None]},{"color":"red"}])
def test_invalid_room_rejected(changes):
    with pytest.raises(DomainError):
        Room.from_input(dict(name="Raum",capacity=4,location="EG",equipment=[],color="blue") | changes,"r")


def test_room_equipment_deduplicated():
    room = Room.from_input(dict(name="Raum",capacity=4,location="EG",equipment=["Beamer","Beamer"]),"r")
    assert room.equipment == ("Beamer",)
