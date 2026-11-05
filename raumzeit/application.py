"""Anwendungsfälle und Geschäftsregeln. Transaktionen umfassen Prüfen und Schreiben."""

from dataclasses import asdict, replace
from datetime import date, timedelta
from uuid import uuid4
from .domain import Booking, BookingDraft, DomainError, Room, integer_value
from .ports import UnitOfWorkFactory


class PlannerService:
    def __init__(self, uow_factory: UnitOfWorkFactory):
        self.uow_factory = uow_factory

    def list_rooms(self) -> list[dict]:
        with self.uow_factory() as uow:
            return [room.to_dict() for room in uow.rooms.list()]

    def save_room(self, data: dict, room_id: str | None = None) -> dict:
        room = Room.from_input(data, room_id or str(uuid4()))
        with self.uow_factory(write=True) as uow:
            if room_id:
                previous = uow.rooms.get(room_id)
                self._check_version(data, previous, "Der Raum")
                if uow.bookings.largest_group(room_id) > room.capacity:
                    raise DomainError("Eine bestehende Buchung benötigt mehr Plätze. Bitte zuerst die Buchung anpassen.", "conflict", "capacity")
                room = replace(room, version=previous.version + 1)
            uow.rooms.save(room, updating=room_id is not None)
        return room.to_dict()

    def list_bookings(self, start: str, end: str, room_id: str | None = None) -> list[dict]:
        try:
            first, last = date.fromisoformat(start), date.fromisoformat(end)
        except (TypeError, ValueError) as exc:
            raise DomainError("Bitte einen gültigen Zeitraum angeben.") from exc
        if not timedelta(0) < last - first <= timedelta(days=31):
            raise DomainError("Der Zeitraum muss zwischen 1 und 31 Tagen liegen.")
        with self.uow_factory() as uow:
            if room_id:
                uow.rooms.get(room_id)
            return [x.to_dict() for x in uow.bookings.list_between(first.isoformat(), last.isoformat(), room_id)]

    def save_booking(self, data: dict, booking_id: str | None = None) -> dict:
        draft = BookingDraft.from_input(data)
        with self.uow_factory(write=True) as uow:
            previous = uow.bookings.get(booking_id) if booking_id else None
            if previous:
                self._check_version(data, previous)
                if previous.status != "active":
                    raise DomainError("Eine stornierte Buchung kann nicht geändert werden.", "conflict")
            room = uow.rooms.get(draft.room_id)
            if draft.participants > room.capacity:
                raise DomainError(f"Der Raum bietet höchstens {room.capacity} Plätze.", field="participants")
            conflict = uow.bookings.conflict(draft.room_id, draft.start, draft.end, booking_id)
            if conflict:
                raise DomainError(f"Der Raum ist von {conflict.start[11:]} bis {conflict.end[11:]} bereits gebucht. Bitte eine andere Zeit oder einen anderen Raum wählen.", "conflict", "start")
            booking = Booking(booking_id or str(uuid4()), **asdict(draft), version=previous.version + 1 if previous else 1)
            uow.bookings.save(booking, updating=previous is not None)
        return booking.to_dict()

    def cancel_booking(self, booking_id: str, data: dict) -> dict:
        with self.uow_factory(write=True) as uow:
            previous = uow.bookings.get(booking_id)
            self._check_version(data, previous)
            if previous.status == "cancelled":
                return previous.to_dict()
            booking = replace(previous, status="cancelled", version=previous.version + 1)
            uow.bookings.save(booking, updating=True)
        return booking.to_dict()

    @staticmethod
    def _check_version(data: dict, booking: Booking | Room, subject: str = "Die Buchung") -> None:
        expected = integer_value(data, "version", "Die Versionsnummer", 2_147_483_647)
        if expected != booking.version:
            raise DomainError(f"{subject} wurde zwischenzeitlich geändert. Bitte den Dialog schließen, die Seite neu laden und erneut versuchen.", "stale")
