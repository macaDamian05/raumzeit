# Dokumentation der KI-Nutzung

Stand: 29.10.2026; ursprüngliche Bearbeitung am 19.10.2026. Werkzeug: OpenAI Codex im Chat. Eine genaue Modell- oder Produktversionskennung wurde für diesen Nachweis nicht unabhängig erfasst. Die KI war an Planung, Quellcode, Tests, Recherche und Dokumentation beteiligt. KI-gestützte technische Läufe und die persönlichen Funktionsprüfungen des Studierenden werden getrennt dokumentiert. Seine Reflexion ist persönlich geprüft, überarbeitet und freigegeben; Nachweise stehen in Anhang D.

## Prompt-Log mit Originalauszügen

Die nachstehenden Zitate sind tatsächlich im verfügbaren Gespräch enthaltene Nutzereingaben. Verkürzungen sind als Auszug gekennzeichnet. Dies ist ein kuratiertes fachliches Prompt-Log und kein unveränderter technischer Export sämtlicher Chat- und Werkzeugnachrichten. Für einen vollständigen Gesprächsnachweis ist vor Abgabe zusätzlich der Originalchat zu sichern. Die folgende Dokumentation enthält keine erfundenen Zwischenprompts.

| ID | Originaleingabe des Studierenden | Ergebnis und verwendete Teile | Nachweis und Prüfung |
|---|---|---|---|
| P01 | „ich möchte erstmal mit dir das vorgehen und die herangehensweise planen schreibe mir bitte ebenfalls eine kurze antwort mail“ (Auszug) | Unterlagen ausgewertet, Anforderungen zusammengefasst, E-Mail-Entwurf erstellt | Auftrag gegen übermittelte Mail geprüft; kein E-Mail-Versand |
| P02 | „du machst das doch sowieso also ist das doch egal - aber ich mag python am meisten“ (Antwort im Planungsdialog) | Python als bevorzugte Sprache festgehalten | Umfang und Erklärung der Architektur auf eine kleine Anwendung begrenzt |
| P03 | „also lager und nachbestellung ist wahrscheinlich zu nah am ehemaligen projekt - aber genaueres zum ablauf und möglichen themenvorschlägen können wir ja in die mail hauen und dann soll hartenstein sagen was wir machen oder?“ | Neues Thema; zwei Vorschläge für die Betreuerabstimmung | Kein Quellcode oder Text aus dem Gruppenbericht übernommen |
| P04 | „hartenstein meinte beide themen sind super also entscheide du welches cooler wäre“ | Raumbuchungssystem ausgewählt | Zustimmung des Betreuers liegt hier nur als Bericht des Studierenden vor |
| P05 | „alles klar du hast die anforderungen was da alles drin sein muss und wie die projektdoku oder so aussehen soll also kanns losgehen“ (Auszug; anschließend vollständige Bewertungsmatrix) | Umsetzung von Anwendung, Tests und Portfolio; Matrix in die Struktur aufgenommen | Quellenabgleich, Akzeptanztests, echter Browser, dokumentierter Fehlerlauf und Wiederholung |

## P06 Überarbeitung nach unabhängiger Bewertung am 29.10.2026

Originalauszug: „Bitte prüfe die Befunde zunächst selbst und setze die technischen und dokumentarischen Verbesserungen anschließend um“. Der Auftrag umfasst CSRF, Raumversionen, Browsertests, Lesbarkeit, Abhängigkeiten und Portfolio; vollständiger Wortlaut: docs/review_auftrag.md.

Ergebnis und Prüfung: Der Assistent führte zuerst die vorhandene Suite aus und reproduzierte anschließend beide Defekte mit neuen, zunächst fehlgeschlagenen Regressionstests. Danach ergänzte er ASCII-Prüfung, Raumversionen, Migration, lesbare Frontendformatierung und wiederholbare Playwright-Fälle in zwei Viewports. Neue Zahlen stammen aus den aktuellen Berichten; alte Ergebnisse bleiben erkennbar archiviert. Die vorhandenen Datenbanken wurden für eine zusätzliche Migrationsprüfung nur lesend geöffnet und ihre Kopien verändert.

Zu diesem Zeitpunkt war die persönliche Prüfung noch offen; die Aufgaben P1–P6 bereiteten sie vor. Die späteren tatsächlichen Rückmeldungen und die Freigabe sind in P08 und Anhang D dokumentiert.

## P07 Abgabefassung und persönliche Prüfung vorbereiten am 29.10.2026

Originalauszug: „Leite mich anschließend schrittweise durch P1–P6. Gib mir konkrete Bedienaufgaben und Verständnisfragen und warte auf meine tatsächlichen Beobachtungen und Antworten.“ Vollständige Anweisung: docs/abschlussauftrag.md.

Ergebnis und Prüfung: Der Assistent reproduzierte den E06-Fehler einzeln auf frischer Datenbank (e06-before.xml), ergänzte eigene Vergleichsdaten und prüfte E06 danach separat in Desktop und Mobil (e06-desktop-alone.xml, e06-mobile-alone.xml). Anschließend bestanden alle zwölf Browserausführungen. Der P3-Sollzustand wurde auf den stornierten ersten Termin und den weiterhin aktiven Anschlusstermin präzisiert; die ADR-Anzahl wurde auf sechs korrigiert. Der Abgabeabgleich steht in docs/abgabecheck.md. Danach führte der Studierende die persönlichen Kontrollen durch und gab die überarbeitete Reflexion frei.

## P08 Persönliche Überarbeitung und Freigabe am 29.10.2026

Originalauszug: „Ich habe die persönliche Reflexion selbst überarbeitet. Bitte verwende die aktuell gespeicherte Fassung als meine freigegebene Endfassung und ändere ihren Inhalt nicht eigenständig.“ Außerdem: „Aktualisiere den Vorspann und die Statusangaben zutreffend: KI-gestützt formuliert, von mir persönlich geprüft und überarbeitet.“

Ergebnis und Prüfung: Der Assistent las und sicherte die gespeicherte Datei, aktualisierte ausschließlich Vorspann und Statusüberschrift und übernahm den freigegebenen Text samt Grenzabschnitt unverändert. Inhaltsprüfsummen und PDF-Textvergleich sichern diese Übernahme ab. Die persönlichen Bedienrückmeldungen und der selbst gestartete 118-Test-Lauf sind getrennt von den KI-gestützten Abschlussläufen dokumentiert. Die zusätzliche persönliche Code-Durchsicht blieb ausgelassen. Es werden keine weiteren Tätigkeiten oder Lernerfahrungen ergänzt.

## Vom Assistenten gewählte und ausgeführte Arbeitsschritte

Diese Schritte sind Arbeitsaufzeichnungen des Agenten, keine nachträglich erfundenen Nutzereingaben:

- Lokalen modularen Monolithen entworfen, Repository-Verträge und Unit of Work eingesetzt; Alternativen in ADRs begründet.
- Zeitregeln, Kapazitätsprüfung, Status und Versionsprüfung implementiert.
- Kalender, Buchungsdialog, Raumansicht, Filter und Historie erstellt; keine externen Gestaltungsassets oder kostenpflichtigen Dienste eingesetzt.
- Unit- und Integrationstests aus fachlichen Gegenbeispielen erstellt, ausgeführt und tatsächliche Fehler behoben. Die erste Ausführung mit vollständig nutzbarer Testumgebung ergab 84 bestandene und vier fehlgeschlagene Tests. Das frühere JUnit-Ergebnis ist erhalten.
- Quellen der Hersteller beziehungsweise Originalautoren geöffnet und mit Implementierungsaussagen verglichen. Die verwendeten Quellen sind in `docs/quellen.json` nachgewiesen.
- Lokalen Browserablauf einschließlich Konflikt und Stornierung ausgeführt. Diese Prüfung ist keine vom Studierenden ausgeführte manuelle Abnahme.
- Dokumententwurf aus Projektdateien und Messwerten erstellt. Testzahlen werden aus den Ergebnisdateien übernommen, nicht frei formuliert.

## Wie Ergebnisse geprüft wurden

Anforderungen wurden zuerst als beobachtbare Bedingungen formuliert. Tests prüfen vollständige und partielle Überschneidungen, benachbarte Intervalle, Grenzwerte der Öffnungszeit, Kapazität, fehlende Datensätze, Persistenz, Stornierung, veraltete Versionen und Konkurrenz. SQL-Zugriffe werden gegen echte temporäre SQLite-Dateien geprüft. HTTP-Tests prüfen Statuscodes und CSRF. Die Browserprüfung ergänzt die serverseitigen Tests um tatsächliche Darstellungen und Bedienhandlungen.

Die KI erzeugte auch die Tests. Deshalb ist ein gemeinsamer Denkfehler weiterhin möglich. Die hohe gemessene Python-Abdeckung sagt nicht aus, dass die Spezifikation vollständig oder das JavaScript vollständig geprüft ist. OCP/LSP werden nicht mit einem erfundenen zweiten Adapter belegt. Performance wird ausschließlich im gemessenen lokalen Aufbau beschrieben. Diese Grenzen sind im Portfolio enthalten.

## Persönliche Prüfung und Freigabe

Justin Kolar hat die praktischen Bedienkontrollen zurückgemeldet und die Python-Suite selbst gestartet. Die Reflexion wurde von ihm persönlich überarbeitet und ausdrücklich freigegeben. Sein dokumentierter Prüfumfang und dessen Grenzen stehen in Anhang D; die Rohbelege des persönlichen Testlaufs bleiben separat erhalten. Die Einreichung und der Abgleich nicht vorliegender zusätzlicher Moodle-Vorgaben bleiben persönliche Schritte.
