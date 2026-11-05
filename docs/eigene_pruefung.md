# Persönliche Prüfung und Reflexion

Stand 29.10.2026. Die tatsächlichen Rückmeldungen sind dokumentiert und die persönliche Prüfung ist im ausgewiesenen Umfang abgeschlossen. Die Reflexion wurde KI-gestützt formuliert, vom Studierenden persönlich geprüft, überarbeitet und als gespeicherte Endfassung freigegeben. Für P5 liegt ein Screenshot des selbst gestarteten 118-Test-Laufs vor; die zusätzliche persönliche Code-Durchsicht blieb auf Wunsch ausgelassen. Diese Anleitung bewahrt die Aufgaben und Sollwerte; die tatsächlichen Ergebnisse stehen in docs/pruefung_ergebnisse.md und docs/persoenliche_ergebnisse.json. Sie werden nicht mit den Sollwerten gleichgesetzt.

## P1 Starten und Raum anlegen

Pruefung_starten.cmd doppelklicken und http://127.0.0.1:5052 öffnen. Die eigene Datenbank instance/pruefung.sqlite3 ist von den Demodaten getrennt. Unter Räume verwalten einen Prüfraum mit Kapazität 6 und Standort Eigene Prüfung anlegen; falls vorhanden, prüfen. Der Nutzer hat dafür den Namen Prüfraum Damian verwendet; mit diesem Raum fortfahren. Was erscheint nach dem Speichern? Was bedeutet Kapazität?

## P2 Buchung und Zeitgrenzen prüfen

Am 30.10.2026 im Prüfraum Eigener Funktionstest von 10:00 bis 10:15 mit vier Personen anlegen; im Wochenkalender öffnen. Danach im selben Raum 10:00 bis 10:30 und anschließend 10:15 bis 10:30 versuchen.

Soll: Überschneidung abgelehnt, direkter Anschluss erlaubt. Notiere die tatsächliche Meldung und die Zahl gespeicherter Termine. Warum werden die beiden Versuche unterschiedlich behandelt?

## P3 Ändern, Stornieren und Neustarten

Den ersten Termin auf 10:30 bis 10:45 verschieben, kontrollieren und stornieren. Unter Alle Buchungen nach Stornierte Buchungen filtern. Server mit Strg+C beenden, erneut starten und Stand kontrollieren.

Soll: Der erste Termin ist nicht mehr aktiv und bleibt als storniert in der Historie erhalten, auch nach Neustart. Der in P2 angelegte Anschlusstermin von 10:15 bis 10:30 bleibt aktiv und unverändert. Prüfe beide Datensätze. Beschreibe den Unterschied zwischen Stornieren und Löschen.

## P4 Veralteten Raumdialog prüfen

Den Prüfraum in zwei Tabs zur Bearbeitung öffnen. Im ersten Tab Kapazität auf 8 ändern und speichern. Im alten Dialog des zweiten Tabs nur den Standort ändern und speichern. Meldung lesen; Dialog schließen, neu laden, Kapazität und Standort prüfen.

Soll: Zweiter Versuch abgewiesen; erster Stand erhalten. Erkläre, warum eine Datenbanksperre allein diesen Fall nicht verhindert und wozu die Versionsnummer dient.

## P5 Einen automatisierten Nachweis nachvollziehen

Im Projektordner .\.venv\Scripts\python.exe tools\verify.py ausführen. Tatsächliche Rückmeldung: Der Nutzer hat diesen Lauf gestartet und einen Screenshot mit 118 bestandenen Tests vorgelegt; die Ergebnisdateien sind unter docs/nachweise/P5_Nutzerlauf_2026-10-29 separat gesichert. Der Raum-Regressionsfall ist darin enthalten. Die zusätzlich vorgeschlagene persönliche Erklärung dieses Testcodes wurde auf ausdrücklichen Wunsch des Nutzers ausgelassen. Optional tools\verify_browser.py wiederholen; eine persönliche Durchführung davon ist nicht behauptet.

Was bedeuten Zeilen- und Zweigabdeckung? Warum schließen bestandene Tests weitere Fehler nicht aus? Trenne die Prüfungen des KI-Assistenten von deinen jetzt tatsächlich ausgeführten Kontrollen.

## P6 Eigene Reflexion und Freigabe

Die tatsächlichen Antworten liegen in docs/persoenliche_ergebnisse.json vor; die persönlich überarbeitete und freigegebene Endfassung steht in docs/persoenliche_reflexion.md. Die folgenden Fragen waren Grundlage der Reflexion. Der Nutzer berichtete keine Unklarheiten oder Überraschungen und bewertete die Oberfläche als benutzerfreundlich. Eine zusätzliche Lernerfahrung wird nicht behauptet.

1. Welche Designentscheidung kannst du an einem konkreten Ablauf begründen?
2. Welche Beobachtung hat dein Verständnis verändert oder eine Unklarheit aufgedeckt?
3. Welchen KI-Vorschlag hast du selbst korrigiert oder nachgeprüft? Falls keinen: ehrlich festhalten.
4. Welche Grenzen würdest du dem Betreuer benennen?
5. Stimmen Quellen, KI-Offenlegung und persönliche Tätigkeiten mit deiner Bearbeitung überein?

Vor Abgabe Moodle-Vorgaben und persönliche Angaben abgleichen. Keine stellvertretend unterzeichnete Eigenständigkeitserklärung. Der etwa 15-minütige Kolloquiumstermin ist noch abzustimmen.

