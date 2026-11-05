"""Reproduzierbare Beispieldaten. Ausschließlich für eine getrennte Demo-Datenbank."""

from datetime import date, timedelta
from .application import PlannerService


def seed_demo(service: PlannerService, today: date | None = None) -> None:
    if service.list_rooms():
        return
    monday = (today or date.today())
    monday -= timedelta(days=monday.weekday())
    rooms = [
        ("Horizont", 12, "1. OG · Ostflügel", ["Bildschirm", "Whiteboard", "Videokonferenz"], "blue"),
        ("Atelier", 8, "EG · Innenhof", ["Whiteboard", "Beamer"], "teal"),
        ("Forum", 24, "2. OG · Westflügel", ["Beamer", "Videokonferenz"], "purple"),
        ("Fokus", 4, "1. OG · Innenhof", ["Bildschirm"], "amber"),
    ]
    created = [service.save_room(dict(name=n, capacity=c, location=l, equipment=e, color=co)) for n,c,l,e,co in rooms]
    samples = [
        (0,0,"09:00","10:00","Wochenauftakt","Alex Berger",8),
        (1,0,"10:30","12:00","Design Workshop","Kim Weber",6),
        (2,0,"14:00","15:30","Projektpräsentation","Sam Neumann",18),
        (0,1,"09:30","11:00","Sprintplanung","Alex Berger",10),
        (3,1,"13:00","14:00","Konzeptarbeit","Kim Weber",3),
        (1,1,"15:00","16:00","Ideenrunde","Robin Fischer",5),
        (2,2,"10:00","12:00","Team Austausch","Sam Neumann",16),
        (0,2,"13:30","15:00","Kundenworkshop","Robin Fischer",8),
        (3,3,"09:00","10:00","Fokuszeit","Kim Weber",2),
        (1,3,"11:00","12:30","Prototypen Review","Alex Berger",6),
        (0,4,"10:00","11:00","Wochenrückblick","Alex Berger",10),
        (2,4,"13:00","14:30","Wissen teilen","Sam Neumann",20),
    ]
    for room, offset, start, end, title, organizer, participants in samples:
        day = (monday + timedelta(days=offset)).isoformat()
        service.save_booking(dict(room_id=created[room]["id"], title=title, organizer=organizer, participants=participants, start=f"{day}T{start}", end=f"{day}T{end}"))
