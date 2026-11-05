# Vorbereitung auf das Kolloquium

Vorschlag für etwa 15 Minuten einschließlich Nachfragen. Die tatsächliche Form und der Termin sind mit Sandro Hartenstein abzustimmen.

| Zeit | Inhalt | Konkreter Nachweis |
|---|---|---|
| 0–2 Minuten | Problem, Zielgruppe, Umfang | Lokale Raumkoordination; Abgrenzung zur Gruppenarbeit |
| 2–5 Minuten | Anwendung demonstrieren | Raumfilter, neue Buchung, Konflikt, Stornierung |
| 5–8 Minuten | Architektur und Designentscheidungen | Trennung der Module; injizierte Unit of Work; SOLID mit Grenzen |
| 8–11 Minuten | Teststrategie und Ergebnisse | Angrenzende Intervalle; zwei konkurrierende Anfragen; tatsächliches JUnit-Ergebnis |
| 11–13 Minuten | KI-Nutzung und eigene Prüfung | Prompt-Log; große KI-Anteile offenlegen; persönlich ausgeführte Prüfung belegen |
| 13–15 Minuten | Grenzen und Rückfragen | Keine Anmeldung, keine globale Zeitzonenlogik, kein allgemeiner Lastnachweis |

## Fragen zum Üben

1. Warum erkennt ein UNIQUE-Index auf Raum und Beginn nicht jede Doppelbuchung?
2. Warum ist eine Prüfung ausschließlich im Browser unzureichend?
3. Was passiert zwischen Konfliktprüfung und INSERT, wenn zwei Anfragen gleichzeitig eintreffen?
4. Warum darf ein Termin direkt am Ende eines anderen Termins beginnen?
5. Worin unterscheiden sich Datenbanksperre und Versionsprüfung?
6. Was bleibt nach einer fehlgeschlagenen Änderung gespeichert?
7. Was leisten die Python-Tests und die Browserprüfungen jeweils, und was sagt hohe Python-Abdeckung nicht aus?
8. Warum wurden Flask, SQLite und eine lokale Bereitstellung gewählt?
9. Welche Teile stammen von der KI, und was habe ich persönlich überprüft?
10. Was müsste sich vor einem Einsatz als tatsächlich geteiltes Mehrbenutzersystem ändern?

Die Antworten stehen verteilt in den ADRs und im Portfolio. Für die persönliche Vorbereitung eigene Antworten formulieren und an der Anwendung überprüfen.

11. Warum kann compare_digest bei einem falschen Headerzeichen scheitern, und wie wird das vor dem Vergleich behandelt?
12. Warum braucht auch der Raumdialog eine gelesene Versionsnummer, obwohl Schreibzugriffe serialisiert werden?
13. Welche Daten bleiben bei der Migration erhalten, und wie wurde das tatsächlich geprüft?
