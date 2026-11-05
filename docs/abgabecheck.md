# Abgabecheck Raumzeit

Stand: 29.10.2026. Grundlage sind die im Chat übermittelte Betreuermail, die Bewertungsmatrix und die lokal bereitgestellten Kursunterlagen. Dieser Abgleich ergänzt keine unbekannten Prüfungsregeln.

## Verfügbare Vorgaben und zugeordnete Unterlagen

| Vorgabe | Beleg und vorhandene Umsetzung | Stand |
|---|---|---|
| Einzelportfolio als Erweiterung oder eigenständige Anwendung; Gruppenbericht nicht übernehmen | Betreuermail; eigene lokale Anwendung Raumzeit, Abgrenzung in Kapitel 1 und docs/auftrag.md | Persönliche Prüfung dokumentiert, Reflexion persönlich geprüft, überarbeitet und am 29.10.2026 freigegeben; Grenzen bleiben ausgewiesen |
| PDF bis 30.10.2026, circa 10–15 Seiten zuzüglich Anhang | Betreuermail; Zielumfang: zwölf Seiten Haupttext, 15 Seiten einschließlich Titel, Inhalts- und Quellenverzeichnis vor dem Anhang | Abschlussnachweis: output/tests/document_qa.json prüft Haupttext, Seitenzuordnung und Ränder |
| MoSCoW und Akzeptanzkriterien | Kapitel 3–4, Anhang A, docs/anforderungen.json; fachliche Grundlage: Anforderungen-Folien 20–26 | Vorhanden |
| Begründete Architektur und SOLID | Kapitel 5–7; sechs ADRs in docs/entscheidungen.md; Fachkonzepte der Architekturfolien | Vorhanden; veraltete Anzahl vier korrigiert |
| Ausgeführte Tests mit Ergebnissen | Kapitel 9–10, Anhang C; getrennte Python- und Browserberichte, Regressionen, Migration und Messung | Aktuelle Berichte: output/tests/junit.xml sowie output/tests/browser.json; E06-Einzelläufe zusätzlich separat dokumentiert |
| KI-Nutzung, Prompt-Logs und Prüfung der Ergebnisse | Kapitel 11, Anhang B, docs/ki_protokoll.md; persönliche Ergebnisse werden getrennt dokumentiert | Persönlich überarbeitete Endfassung freigegeben; Originalantworten und KI-Anteile getrennt dokumentiert |
| Quellenverzeichnis, beschriftete Tabellen und Abbildungen | Kapitel 11, Quellenverzeichnis, nummerierte Darstellungen | Abschlussnachweis: output/tests/document_qa.json bestätigt die tatsächliche KI-Sichtprüfung aller gerenderten Seiten |
| Bewertung: Projektmanagement 20 %, Inhalt 50 %, Struktur/Argumentation 20 %, Formales 10 % | Kapitel 2 mit Matrixbezug, docs/projektverlauf.md; inhaltliche Nachweisketten, begründete Methodik und Quellenarbeit | Zugeordnet; keine Note oder Anerkennung vorweggenommen |
| Kolloquium circa 15 Minuten nach Abgabe | Betreuermail; docs/kolloquium.md | Termin mit Betreuer abzustimmen |

## Aus den verfügbaren Unterlagen nicht belegbar

- Die vollständigen Anforderungen „Projektbericht SE 2026“ bzw. eine aktuelle Moodle-Abgabeanweisung liegen nicht als eigenständiges Dokument vor. Keine Aussage, dass alle unbekannten Vorgaben bereits erfüllt seien.
- Nicht angegeben sind Abgabeweg bzw. Empfänger/Uploadstelle und die genaue Uhrzeit am 30.10.2026.
- Nicht angegeben sind verbindliche Dateinamen und ob neben dem PDF auch Quellcode, ZIP oder weitere Nachweise hochgeladen werden müssen. Das vorbereitete ZIP ist eine ergänzende Projektlieferung, keine behauptete Pflicht.
- Nicht ausdrücklich präzisiert ist, welche Verzeichnisse zum Seitenumfang zählen. Der dokumentierte bisherige Stand liegt sowohl mit zwölf Haupttextseiten als auch mit 15 Seiten vor dem Anhang im genannten Rahmen; nach dem Neubau erneut prüfen.
- Eine verbindliche Formatvorlage, vorgeschriebene Zitiernorm, zusätzliche Pflichtangaben auf dem Titelblatt oder ein verbindlicher Wortlaut einer Eigenständigkeits-/KI-Erklärung sind aus den verfügbaren Angaben nicht ersichtlich. Solche Regeln nur übernehmen, wenn tatsächlich bereitgestellt; eine persönliche Unterschrift kann der Assistent nicht ersetzen.
- Ein bestätigter Kolloquiumstermin liegt nicht vor. Die Themenzustimmung ist als Bericht des Studierenden, nicht als weitere Originalmail dokumentiert.

Die Einführungsvorlesung 2025 (PDF 1-1, Seite 8) beschreibt Gruppen-Pitch, Abschlusspräsentation und Dokumentation mit anderen Anteilen und Terminen. Diese historische Gruppenbewertung wird nicht auf die ausdrücklich vereinbarte Einzelabgabe 2026 übertragen. Die alte Gruppen-Projektdokumentation ist ein Vorprojekt, keine zusätzliche Abgabeordnung.

## Abschluss und verbleibende persönliche Schritte

Die persönliche Prüfung ist im dokumentierten Umfang abgeschlossen. Der Studierende gab seine selbst überarbeitete Reflexion ausdrücklich als gespeicherte Endfassung frei. Die zusätzliche persönliche Code-Durchsicht blieb auf Wunsch ausgelassen; eine vollständige unabhängige Code- oder Quellenprüfung wird nicht behauptet.

Der finale Quellstand wird durch Python- und Browsermanifeste abgesichert. Der PDF-Bau übernimmt aktuelle Berichte und prüft die freigegebene Reflexion per SHA-256. Die PDF-Kontrolle prüft deren vollständige Textübernahme, Seitenumfang und Ränder, rendert alle Seiten und protokolliert die tatsächlich ausgeführte Sichtprüfung. Die Archivierung akzeptiert ausschließlich dazu passende Quellen und Prüfnachweise; der ZIP-Inhalt wird auf CRC-Fehler geprüft.

Für die Einreichung: output/portfolio/Portfolio_Justin_Kolar_Raumzeit.pdf. Ergänzende Projektlieferung: output/dist/Raumzeit_Projekt.zip und output/dist/Pruefsummen.json. Der persönliche Testlauf bleibt separat unter docs/nachweise erhalten; ältere Arbeitsstände sind lokal unter output/history gesichert und nicht Teil des aktuellen Archivs.

Vor der tatsächlichen Einreichung muss der Studierende die nicht vorliegenden aktuellen Moodle-Vorgaben, Abgabeweg/Empfänger und genaue Uhrzeit prüfen. Zusätzliche Pflichtangaben, Erklärungen oder Unterschriften sind nur erforderlich, wenn die tatsächliche Abgabeanweisung sie verlangt. Aus den verfügbaren Unterlagen sind keine weiteren konkreten Pflichtangaben belegbar. Der Kolloquiumstermin ist noch abzustimmen. Es wurde nichts eingereicht oder versandt.
