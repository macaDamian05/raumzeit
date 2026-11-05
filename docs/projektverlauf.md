# Projektverlauf und Arbeitsorganisation

## Arbeitsweise

Einzelprojekt mit KI-Unterstützung; Arbeitspakete werden nach Ergebnis statt nach fiktiven Arbeitsstunden verfolgt. Der Studierende verantwortet Themenabstimmung, Anforderungen, fachliche Schlussprüfung und Abgabe. Die in dieser Sitzung ausgeführten technischen Arbeiten übernimmt der KI-Assistent. Es werden weder Teamrollen noch Nutzerinterviews erfunden.

## Baseline und tatsächlicher Stand

Die folgenden Termine sind Plantermine, die zu Beginn der Implementierung aus der Abgabefrist abgeleitet wurden. Ein früh fertiggestelltes KI-Arbeitspaket ist keine bereits absolvierte persönliche Lern- oder Prüfzeit.

| Meilenstein | Zieltermin | Abnahmekriterium | Tatsächlicher Stand |
|---|---|---|---|
| M1 Auftrag und Thema | 19.10.2026 | Thema und Umfang festgehalten | 19.10.2026 dokumentiert; Themenzustimmung laut Chat des Studierenden |
| M2 Architektur und Anwendung | 22.10.2026 | Kernfälle lokal ausführbar | Technische Arbeitsfassung 19.10.2026 erstellt |
| M3 Verifikation | 24.10.2026 | Fachregeln, Persistenz und Nebenläufigkeit geprüft | Automatische Tests und Browserprüfung 19.10.2026 ausgeführt; Ergebnisdateien vorhanden |
| M4 Portfolioentwurf | 27.10.2026 | Anforderungen, Quellen, Architektur und Ergebnisse enthalten | KI-gestützte Arbeitsfassung 19.10.2026 erstellt |
| M5 Persönliche Prüfung | 29.10.2026 | Anwendung selbst vorgeführt, Regeln erklärt, Text und KI-Angaben geprüft | Offen; durch Justin Kolar auszuführen |
| M6 Abgabe | 30.10.2026 | Geprüftes PDF eingereicht | Offen; kein Versand durch den Assistenten |
| M7 Kolloquium | Nach Abgabe | Termin vereinbart und Gespräch geführt | Offen; Termin mit Betreuer abzustimmen |

## Kommunikation und Entscheidungen

- Der Studierende übermittelte die Vorgaben für die Einzelabgabe und bat zunächst um Planung und einen E-Mail-Entwurf.
- Der Assistent formulierte zwei Themenvorschläge; der Studierende berichtete anschließend von der positiven Rückmeldung des Betreuers.
- Der Studierende bevorzugte Python und die lokale Browseroberfläche. Er delegierte die Themenwahl und gab anschließend die Umsetzung frei.
- Die ergänzte Bewertungsmatrix wurde vor der Implementierung in die Dokumentationsstruktur aufgenommen.
- Ein Zugriff auf Moodle oder ein tatsächlicher E-Mail-Versand durch den Assistenten fand nicht statt.

## Risiken

| Risiko | Einschätzung zu Beginn | Gegenmaßnahme | Restliches Risiko |
|---|---|---|---|
| Umfang übersteigt verfügbaren Zeitraum | Hoch | MoSCoW; fester lokaler Funktionsumfang; keine Cloud- oder Serienfunktion | Änderungen am Umfang nur nach Aufwandseinschätzung |
| Zwei Buchungen werden gleichzeitig akzeptiert | Hoch | BEGIN IMMEDIATE über Konfliktprüfung und Schreibvorgang; konkurrierender Test mit zwei Verbindungen | SQLite serialisiert Schreibzugriffe; große Mehrbenutzerlast nicht untersucht |
| KI-Code und KI-Tests bestätigen denselben Fehler | Hoch | Akzeptanzkriterien zuerst; Grenzfälle, Gegenbeispiele, echte SQLite-Integration, Browserprüfung und Quellenabgleich | Persönliche unabhängige Kontrolle bleibt offen |
| Verlust oder Verwechslung der Daten | Mittel | Demo getrennt; Testdatenbanken isoliert; Hinweise zur Sicherung der lokalen Datenbank | Keine automatische Datensicherung |
| Nachträgliche 2026-Vorgaben fehlen | Mittel | Verfügbare Mail und Matrix als Baseline dokumentieren; keine Vollständigkeit unbekannter Moodle-Regeln behaupten | Zusätzliche Vorgaben vor Abgabe abgleichen |
| Oberfläche außerhalb der Testumgebung abweichend | Mittel | Prüfung bei Desktopbreite und 390-Pixel-Viewport; lokale Assets | Keine vollständige Prüfung aller Browser oder assistiven Technologien |

## Tatsächliche Iteration am 19.10.2026

1. Projektgerüst, Datenmodell und Fachregeln angelegt; technische Abhängigkeiten in einer eigenen virtuellen Umgebung installiert.
2. Das im Sandbox-Temporärverzeichnis blockierte pytest-Setup wurde auf ein neues Verzeichnis im Projekt umgestellt. Dies war ein Umgebungsproblem, kein Nachweis eines Anwendungsfehlers.
3. Der erste vollständig ausführbare Lauf ergab 84 bestandene und vier fehlgeschlagene Tests. Die Ausstattungsdaten waren in internen Rückgaben Tupel, in Eingaben aber Listen. Außerdem verdeckte die CSRF-Prüfung bei einer unbekannten HTTP-Methode den erwarteten 405-Fehler.
4. Rückgaben wurden vereinheitlicht und die CSRF-Prüfung auf tatsächlich aufgelöste Änderungsrouten begrenzt. Die vier betroffenen Fälle und die gesamte bestehende Suite wurden danach erneut ausgeführt. Der frühere Lauf ist in `output/tests/iteration-01.xml` erhalten.
5. Die Browserprüfung bestätigte unter anderem Konfliktmeldung, direkt anschließende Buchung, Änderung, Stornierung, Historie und Raumfilter. Messergebnisse und Screenshots wurden gespeichert.

Der aktuelle maschinenlesbare Stand ist in `output/tests/` abgelegt. Es werden keine ausgedachten täglichen Tätigkeiten bis zum Abgabetermin nachgetragen.


## KI-gestützte Überarbeitung am 29.10.2026

Auslöser ist die vom Nutzer übermittelte unabhängige Bewertung, keine neu behauptete Betreuernachricht. Die bestehende Suite wurde zuerst erneut ausgeführt: 88 Tests bestanden. Zwei zusätzliche Regressionstests bestätigten anschließend die gemeldeten Fehler: TypeError bei Token ä und HTTP 200 mit verlorenem Raumstand. Der Fehlerlauf liegt in output/tests/review-before.xml.

Der Assistent ergänzte ASCII-Prüfung, Raumversionen über Datenbank, Service, API und Dialog sowie die Schema-Migration. Der Altbestand bleibt über eine additive Änderung nutzbar. Tests prüfen auch parallele Raumänderungen und den unveränderten Stand nach Konflikten. Eine Wiederholung der Initialisierung wurde geprüft; die vorhandenen Originaldatenbanken wurden dabei nur lesend geöffnet und ihre Kopien migriert.

HTML, CSS und JavaScript wurden mit festgelegter Prettier-Version lesbar formatiert. Die Dokumentenwerkzeuge einschließlich transitiver Python-Pakete wurden separat fixiert. Die Browserprüfung wurde von einmaligen Bedienhandlungen auf sechs wiederholbare Szenarien in zwei Viewports umgestellt. Im Testaufbau wurden ein von Chromium gesperrter Port und ein uneindeutiger Datentitel korrigiert; diese Einrichtungsfehler werden nicht als Anwendungsfehler ausgegeben.

Die aktuellen Zahlen werden aus den tatsächlich erzeugten Berichten übernommen. Historische Ergebnisse bleiben unter output/history/2026-10-19 erhalten und werden nicht als neue Prüfungen ausgegeben. Es werden keine persönlichen Tätigkeiten zwischen dem 19. und 29.10. ergänzt. Persönliche Durchführung, Reflexion und Freigabe sind weiterhin offen.

## Weitere Abgabeprüfung am 29.10.2026

Auftrag: docs/abschlussauftrag.md. Die technischen Korrekturen und Prüfungen führte der KI-Assistent aus. E06 scheiterte ohne vorherige Browserfälle an einer nicht selbst angelegten Vergleichsbuchung. Der isolierte Fehlerlauf ist in output/tests/e06-before.xml erhalten. Der Fall erstellt nun seinen Vergleichsraum und beide Buchungen selbst über die Oberfläche und kontrolliert deren tatsächliches Ein- und Ausblenden. Danach bestanden Desktop-E06 und Mobil-E06 jeweils allein auf einer frischen Datenbank sowie anschließend alle zwölf Ausführungen der kompletten Suite. JavaScript-Syntax- und Frontend-Formatprüfung bestanden ebenfalls.

Die persönliche Anleitung berücksichtigt nun den nach P3 weiterhin aktiven Anschlusstermin von 10:15 bis 10:30. Die Textquelle nennt sechs ADRs; die übrigen historischen Testzahlen sind als frühere Läufe gekennzeichnet und bleiben erhalten. Zusätzliche Abgabevorgaben wurden nicht erfunden; verfügbare und fehlende Informationen sind in docs/abgabecheck.md getrennt.

P1–P6 werden anschließend schrittweise mit dem Studierenden durchlaufen. Bis zu tatsächlichen Antworten bleiben alle persönlichen Ergebnisse offen. Der Abschlusslauf, PDF-Neubau, Sichtprüfung und neue Archivierung folgen nach der persönlichen fachlichen Freigabe. Die bisherigen PDF-/ZIP-Dateien bleiben bis dahin der ältere Arbeitsstand.

Die Bewertungsmatrix wird konkret bedient: Prozess und Korrekturschleife (20 % Projektmanagement), begründete Implementierung mit Nachweisen (50 % Inhalt), nachvollziehbare Anforderung-Entscheidung-Test-Ketten (20 % Struktur/Argumentation) sowie einheitliche Quellen und geprüfte PDF-Ausgabe (10 % Formales). Daraus wird keine Note oder Notengarantie abgeleitet.

## Erste persönliche Rückmeldung am 29.10.2026

Der Nutzer meldete den Start positiv zurück und fügte einen Screenshot der Raumverwaltung bei. Er zeigt Prüfraum Damian mit Kapazität sechs und Standort Eigene Prüfung. Die Aussage zum vorherigen Buchungstest ist allgemein positiv; einzelne Buchungsversuche und Meldungen sind noch nicht mitgeteilt. Die Bildauswertung nahm der KI-Assistent vor. Es werden weder eine eigene fachliche Erklärung noch abgeschlossene P2–P6 oder eine Freigabe daraus abgeleitet. Die Rückmeldung und ihre Grenzen sind in docs/persoenliche_ergebnisse.json gespeichert.

In der anschließenden Rückmeldung erklärte der Nutzer, bei sieben Personen solle eine Meldung über die überschrittene Raumkapazität erscheinen. Als mögliche Verbesserung nannte er die Empfehlung eines passenden anderen Raums. Diese Idee wird als Nutzervorschlag festgehalten, ohne eine zusätzliche Funktion umzusetzen. Zusammen mit der ersten Bedienrückmeldung ist damit P1 dokumentiert. Zu P2 berichtete er für die vorgegebenen Versuche 10:00–10:15, 10:00–10:30 und 10:15–10:30 in dieser Reihenfolge „funktioniert“, „fehler“, „funktioniert“. Der Fehlertext und die eigene fachliche Erklärung der Intervalle sind noch offen; keine automatische Prüfung oder Kenntnis eines HTTP-Status wird daraus abgeleitet. P3–P6, Reflexion und Gesamtfreigabe bleiben offen.

Danach teilte der Nutzer den genauen Konflikttext mit: „Der Raum ist von 10:00 bis 10:15 bereits gebucht. Bitte eine andere Zeit oder einen anderen Raum wählen.“ Er begründete Anschlusstermine mit praktischen Gesprächsfolgen und einem möglicherweise früheren Gesprächsende. Der Assistent präzisierte, dass die gespeicherte Endzeit zählt und ein tatsächlich früheres Ende die Reservierung nicht automatisch ändert. Diese Erklärung wird ausdrücklich als KI-Erläuterung dokumentiert, ohne dem Nutzer eine eigene korrigierte Erklärung oder Lernerfahrung zuzuschreiben. Die P2-Bedienprüfung ist damit zurückgemeldet; zur fachlichen Reflexion bleibt diese Unterscheidung abzugleichen. Als nächster Schritt wurde P3 angeleitet; eine Durchführung oder Freigabe wird noch nicht behauptet.

Auf die P3-Anleitung zu Bearbeiten, Stornieren und Neustarten antwortete der Nutzer zusammenfassend „ist alles richtig“. Er schlug zusätzlich vor, stornierte Termine wiederherstellen zu können. Diese Rückmeldung wird als persönliche Bestätigung des angeleiteten Ablaufs und als konkrete Verbesserungsidee dokumentiert. Es wird keine neue Funktion implementiert; eine eigene Definition von Stornieren versus Löschen bleibt noch abzugleichen. Anschließend wird P4 mit zwei gleichzeitig geöffneten Raumdialogen angeleitet. P4–P6 und die Gesamtfreigabe bleiben offen.

Nach P4 nannte der Nutzer die genaue Meldung zum zwischenzeitlich geänderten Raum und bestätigte den Ablauf allgemein. Als Begründung für den Schutz benannte er das mögliche Überschreiben durch den alten Dialog (possible override). Die genauen Feldwerte nach dem Neuladen und ein HTTP-Status wurden nicht eigens berichtet und werden nicht als persönlich abgelesen behauptet. P4 ist auf dieser Grundlage dokumentiert. Anschließend wird P5 zur eigenen Ausführung der Testsuite und zum Nachvollziehen eines Regressionstests angeleitet. P5, P6 und die fachliche Gesamtfreigabe bleiben offen.

Für P5 legte der Nutzer einen PowerShell-Screenshot seines selbst gestarteten verify.py-Laufs vor: 118 Tests bestanden in 2,12 Sekunden; die Python-Abdeckung wird gerundet mit 99 % angezeigt. Der Assistent glich die vorhandenen Berichte ab und sicherte diesen Nutzerlauf einschließlich Screenshot gesondert unter docs/nachweise/P5_Nutzerlauf_2026-10-29, damit spätere Abschlussläufe ihn nicht ersetzen. Der Raum-Regressionsfall war in diesem Gesamtlauf enthalten. Die zusätzliche persönliche Code-Durchsicht und Erklärung der Assertion wird auf ausdrücklichen Wunsch des Nutzers ausgelassen. Sie wird weder als durchgeführt noch als eigene Codeprüfung ausgewiesen. Persönliche Reflexion und fachliche Freigabe stehen weiterhin aus; P6 wird als nächster Schritt angeleitet.

Bei P6 verwies der Nutzer für Anschlusstermine auf seine frühere Antwort und erlaubte eine sprachliche Ergänzung. Zu Stornierungen erklärte er, dass die Buchung für eine mögliche spätere Wiederherstellung gespeichert bleibt, während Löschen diese Grundlage entfernt. Er berichtete keine Unklarheiten oder Überraschungen und bewertete die Oberfläche als benutzerfreundlich. Auf dieser tatsächlichen Grundlage erstellte der Assistent docs/persoenliche_reflexion.md als Entwurf zur Freigabe. Die Endzeitregel wird darin fachlich präzisiert und als KI-Ergänzung ausgewiesen. Es werden keine neue Lernerfahrung, vollständige Codeprüfung oder persönliche Quellenprüfung behauptet. Die fachliche Freigabe und der anschließende technische Abschluss stehen noch aus.

## Persönliche Freigabe und Abgabefassung am 29.10.2026

Der Studierende teilte mit, dass er die persönliche Reflexion selbst überarbeitet hat, und gab ausdrücklich die aktuell gespeicherte Fassung als Endfassung frei. Er verlangte die unveränderte Übernahme und die Kennzeichnung als KI-gestützt formuliert, persönlich geprüft und überarbeitet. Der Assistent sicherte die Ausgangsdatei, aktualisierte nur Vorspann und Statusüberschrift und prüfte die unveränderten Inhalte per Prüfsumme. Die dokumentierten Grenzen der persönlichen Prüfung bleiben erhalten.

Nach der Freigabe werden die automatisierten Abschlussprüfungen erneut ausgeführt, die Berichte auf denselben Quellstand bezogen und die PDF mit der freigegebenen Reflexion erzeugt. Seitenumfang, vollständige Textübernahme, visuelle Darstellung und Archivkonsistenz sind technische Abnahmekriterien. Die tatsächlichen Endergebnisse stehen in output/tests und output/dist/Pruefsummen.json. Einreichung und Terminabstimmung verbleiben beim Studierenden; keine zusätzliche Kommunikation wird behauptet.
