"""Fachliche Daten und Eingaberegeln, unabhängig von Flask und SQLite."""

from dataclasses import asdict, dataclass
from datetime import datetime
import re

EQUIPMENT = ("Bildschirm", "Whiteboard", "Videokonferenz", "Beamer")
COLORS = ("blue", "teal", "purple", "amber", "rose", "slate")


class DomainError(Exception):
    def __init__(self, message: str, code: str = "validation", field: str | None = None):
        super().__init__(message)
        self.code, self.field = code, field


def text_value(data: dict, key: str, label: str, limit: int) -> str:
    raw = data.get(key)
    if not isinstance(raw, str) or not raw.strip():
        raise DomainError(f"Bitte {label} angeben.", field=key)
    value = " ".join(raw.split())
    if len(value) > limit:
        raise DomainError(f"{label} darf höchstens {limit} Zeichen enthalten.", field=key)
    return value


def integer_value(data: dict, key: str, label: str, maximum: int = 500) -> int:
    value = data.get(key)
    if type(value) is not int or not 1 <= value <= maximum:
        raise DomainError(f"{label} muss eine ganze Zahl zwischen 1 und {maximum} sein.", field=key)
    return value


def local_time(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", value):
        raise DomainError("Datum und Uhrzeit bitte vollständig angeben.", field=field)
    try:
        result = datetime.fromisoformat(value)
    except ValueError as exc:
        raise DomainError("Datum oder Uhrzeit ist ungültig.", field=field) from exc
    if result.minute % 15:
        raise DomainError("Buchungen sind im 15-Minuten-Raster möglich.", field=field)
    return result


@dataclass(frozen=True)
class Room:
    id: str
    name: str
    capacity: int
    location: str
    equipment: tuple[str, ...]
    color: str
    version: int = 1

    def to_dict(self) -> dict:
        return {**asdict(self), "equipment": list(self.equipment)}

    @classmethod
    def from_input(cls, data: dict, room_id: str) -> "Room":
        name = text_value(data, "name", "einen Raumnamen", 80)
        location = text_value(data, "location", "einen Standort", 100)
        capacity = integer_value(data, "capacity", "Die Kapazität")
        equipment = data.get("equipment", [])
        if not isinstance(equipment, list) or any(not isinstance(x, str) or x not in EQUIPMENT for x in equipment):
            raise DomainError("Bitte eine gültige Ausstattung auswählen.", field="equipment")
        color = data.get("color", "blue")
        if color not in COLORS:
            raise DomainError("Bitte eine gültige Raumfarbe auswählen.", field="color")
        return cls(room_id, name, capacity, location, tuple(sorted(set(equipment))), color)


@dataclass(frozen=True)
class BookingDraft:
    room_id: str
    title: str
    organizer: str
    participants: int
    start: str
    end: str

    @classmethod
    def from_input(cls, data: dict) -> "BookingDraft":
        room_id = text_value(data, "room_id", "einen Raum", 40)
        title = text_value(data, "title", "einen Titel", 120)
        organizer = text_value(data, "organizer", "eine verantwortliche Person", 100)
        participants = integer_value(data, "participants", "Die Personenzahl")
        start, end = local_time(data.get("start"), "start"), local_time(data.get("end"), "end")
        if start >= end:
            raise DomainError("Das Ende muss nach dem Beginn liegen.", field="end")
        if start.date() != end.date():
            raise DomainError("Eine Buchung muss am selben Tag beginnen und enden.", field="end")
        if start.weekday() >= 5:
            raise DomainError("Räume können von Montag bis Freitag gebucht werden.", field="start")
        if start.hour < 8 or end.hour > 20 or (end.hour == 20 and end.minute):
            raise DomainError("Die Buchungszeiten liegen zwischen 08:00 und 20:00 Uhr.", field="start")
        return cls(room_id, title, organizer, participants, start.isoformat(timespec="minutes"), end.isoformat(timespec="minutes"))


@dataclass(frozen=True)
class Booking:
    id: str
    room_id: str
    title: str
    organizer: str
    participants: int
    start: str
    end: str
    status: str = "active"
    version: int = 1

    def to_dict(self) -> dict:
        return asdict(self)
