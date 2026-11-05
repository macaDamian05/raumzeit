"""Lokale Messung des HTTP-Adapters mit Testclient, ohne Browser und Netzwerk."""

from datetime import date,datetime,timedelta,timezone
from pathlib import Path
import json
import statistics
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from raumzeit.web import create_app


def main():
    folder=ROOT/"output"/"qa"/f"benchmark-{uuid.uuid4().hex[:10]}"
    folder.mkdir(parents=True)
    app=create_app({"DATABASE":str(folder/"benchmark.sqlite3"),"TESTING":True,"SECRET_KEY":"benchmark-only"})
    service=app.extensions["planner"]
    rooms=[service.save_room(dict(name=f"Raum {i+1:02d}",capacity=20,location="Testdaten")) for i in range(10)]
    for room in rooms:
        for day in range(5):
            for slot in range(20):
                start=datetime(2026,10,19,8)+timedelta(days=day,minutes=15*slot)
                service.save_booking(dict(room_id=room["id"],title=f"Messung {slot}",organizer="Benchmark",participants=5,start=start.isoformat(timespec="minutes"),end=(start+timedelta(minutes=15)).isoformat(timespec="minutes")))
    client=app.test_client()
    endpoint="/api/bookings?from=2026-10-19&to=2026-10-26"
    for _ in range(5): client.get(endpoint)
    samples=[]
    for _ in range(100):
        start=time.perf_counter()
        response=client.get(endpoint)
        assert response.status_code==200 and len(response.json["bookings"])==1000
        samples.append((time.perf_counter()-start)*1000)
    result=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),method="Flask-Testclient; Antwort einschließlich JSON-Dekodierung; 5 Aufwärmläufe; 100 Messungen",rooms=10,bookings=1000,samples=100,median_ms=round(statistics.median(samples),3),p95_ms=round(sorted(samples)[94],3),max_ms=round(max(samples),3),target_p95_ms=250)
    result["passed"]=result["p95_ms"]<result["target_p95_ms"]
    target=ROOT/"output"/"tests"/"benchmark.json"
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(result,ensure_ascii=True,indent=2))
    return 0 if result["passed"] else 1


if __name__=="__main__": raise SystemExit(main())
