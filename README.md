# Raumzeit 1.1

Lokales Raumbuchungssystem mit Python, Flask und SQLite für das SE-Einzelportfolio von Justin Kolar. Abgabefassung vom 29.10.2026 mit dokumentierter KI-Unterstützung. Persönliche Funktionsprüfung und eigener Testlauf sind dokumentiert; die Reflexion wurde persönlich geprüft, überarbeitet und freigegeben. Der begrenzte Prüfumfang bleibt ausgewiesen.

## Starten

Die Umgebung ist auf diesem Rechner eingerichtet. Im Projektordner per Doppelklick starten und die ausgegebene Adresse im Browser öffnen:

| Datei | Datenbank | Adresse |
|---|---|---|
| Demo_starten.cmd | instance/demo.sqlite3 | http://127.0.0.1:5050 |
| Starten.cmd | instance/raumzeit.sqlite3 | http://127.0.0.1:5050 |
| Pruefung_starten.cmd | instance/pruefung.sqlite3 | http://127.0.0.1:5052 |

Die beiden ersten Varianten verwenden denselben Port und laufen nacheinander. Beenden mit Strg+C im Serverfenster. Der Browser-Testserver verwendet separat Port 5051 und eigene temporäre Dateien. Die persönliche Prüfung verändert keine Demodaten; der Ablauf steht in docs/eigene_pruefung.md.

Die Demo wird bei ihrem ersten Start mit vier Räumen und zwölf Terminen der dann aktuellen Woche befüllt. Spätere Starts überschreiben keine Daten. Bei einer älteren Demo deshalb zur ursprünglichen Woche navigieren, statt vorhandene Daten zu löschen.

## Einrichtung und getrennte Abhängigkeiten

Geprüft: Windows, Python 3.12.14, Node.js 24.14.0. Die Anwendung benötigt Python ab 3.12. Andere Betriebssysteme sind nicht separat geprüft. Die Erstinstallation benötigt Internet; der laufende Raumplaner verwendet keine externen Dienste.

Einrichtung.cmd erzeugt bei Bedarf eine virtuelle Umgebung und installiert requirements-dev.txt. Alternativ in PowerShell im Projektordner:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m raumzeit --demo
```

Die Abhängigkeiten sind getrennt:

- requirements.txt: tatsächliche App-Laufzeitpakete.
- requirements-dev.txt: zusätzliche Python-Testwerkzeuge.
- requirements-portfolio.txt: ReportLab 4.4.9, Pillow 12.3.0, pypdf 6.10.0, pdfplumber 0.11.9, pypdfium2 5.14.0 und fixierte transitive Dokumentenpakete.
- package.json und package-lock.json: Playwright 1.64.1 und Prettier 3.9.10. Node ist für Browserprüfung und Formatierung erforderlich, nicht für den App-Betrieb.

Dokumentenwerkzeuge separat installieren:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-portfolio.txt
```

Für Browserprüfungen Node.js installieren, dann einmalig:

```powershell
npm ci
npx playwright install chromium
```

Keine globalen npm-Pakete erforderlich. Auf Linux/macOS entsprechend .venv/bin/python verwenden; diese Startvariante ist beschrieben, hier jedoch nicht separat ausgeführt.

## Fachregeln und Versionsschutz

Räume besitzen Namen, Kapazität, Standort, Ausstattung, Farbe und Version. Buchungen haben einen Raum, Titel, verantwortliche Person, Personenzahl, Beginn, Ende, Status und Version. Die verantwortliche Person ist ein Textfeld, keine authentifizierte Identität.

- Mo–Fr, 08:00–20:00 Uhr; Beginn und Ende am selben Tag, 15-Minuten-Raster.
- Lokale Berliner Wandzeit als YYYY-MM-DDTHH:MM; keine Zeitzonenumrechnung. Vergangene Termine sind für Dokumentation zulässig.
- Positive ganze Personenzahl bis zur Raumkapazität, maximal 500.
- Halboffene Intervalle [Beginn, Ende): 09:00–10:00 und 10:00–11:00 sind im selben Raum erlaubt.
- Konfliktprüfung und Schreiben laufen in derselben BEGIN-IMMEDIATE-Transaktion.
- Änderungen an Räumen und Buchungen verlangen die zuvor gelesene positive version. Fehlende oder ungültige Version: HTTP 422. Veraltete Version: 409; der aktuelle Stand bleibt erhalten. Erfolgreiche Änderung: Version um eins erhöhen.
- Stornierte Buchungen bleiben in der Historie, blockieren jedoch keine Zeit. Eine weiterhin aktive Buchung schützt ihre Personenzahl auch nach ihrem Datum gegen eine zu starke Kapazitätsreduzierung.

## Vorhandene Datenbanken und Sicherheit

Anwendung 1.1 ergänzt beim Start atomar rooms.version mit DEFAULT 1 und setzt PRAGMA user_version auf 2. Wiederholte Initialisierung erhält vorhandene Daten und Versionsnummern. Eine unbekannte neuere Schema-Version wird nicht heruntergestuft. Alte Datenbankdateien bleiben mit dem neuen Code nutzbar; alte API-Clients ohne version müssen angepasst werden. Ein Downgrade auf Anwendung 1.0 wird nicht unterstützt.

Vor Übertragung oder Migration den Server beenden und die SQLite-Datei sichern. Bestehende Originaldateien wurden bei der zusätzlichen Migrationsprüfung nur lesend geöffnet; migriert wurden Kopien. Es gibt keine automatische Datensicherung. Sitzungsschlüssel liegen daneben in .secret-Dateien. Laufzeitdateien, Schlüssel und virtuelle Umgebung gehören nicht ins Archiv.

Der Start bindet nur an 127.0.0.1. Hostprüfung, CSRF, Requestgrößenlimit und Sicherheitsheader sind umgesetzt. Nicht-ASCII-Token werden vor compare_digest kontrolliert mit 403 abgewiesen. SQL verwendet Parameter, Nutzereingaben im Frontend werden als Text eingefügt. Lokales HTTP hat keine Transportverschlüsselung; der Entwicklungsserver ist für die lokale Vorführung gedacht. Anmeldung, Rollen, öffentlicher Betrieb, Serienbuchungen und Kalenderexport bleiben außerhalb des Umfangs.

## Prüfungen wiederholen

```powershell
.\.venv\Scripts\python.exe tools\verify.py
.\.venv\Scripts\python.exe tools\verify_browser.py
.\.venv\Scripts\python.exe tools\benchmark.py
npm run check:format
```

verify.py erzeugt JUnit, Python-Zeilen-/Zweigabdeckung und ein Quellmanifest in output/tests. Die Testdatenbanken sind isoliert. verify_browser.py führt sechs Playwright-Szenarien je einmal bei 1280 × 900 und 390 × 844 Pixeln aus. Echte Flask-/SQLite-Verarbeitung, keine API-Mocks; nur der Browser-Datumswert ist auf 26.10.2026 fixiert. Die Tests prüfen Anlegen/Neuladen, Überschneidung, Bearbeiten/Stornieren, Kurztermin, veralteten Raumdialog und Navigation/Filter/Suche. Unbehandelte JavaScript-Ausnahmen lassen die Prüfung ebenfalls scheitern.

Browserdaten: output/playwright/results.json, junit.xml und screenshots/. Die kompakte Auswertung und ein eigenes Quellmanifest stehen unter output/tests. **Python-Abdeckung ist keine JavaScript- oder Browserabdeckung.** Chromium und zwei Viewports sind keine vollständige Browser-/Screenreaderprüfung.

E06 legt seinen Vergleichsraum und beide benötigten Buchungen selbst über die Oberfläche an. Er muss ohne vorherige Fälle funktionieren. Isoliert wiederholen: `npx playwright test --project desktop --grep E06 --reporter=list` und entsprechend mit `--project mobile`. Jeder Aufruf startet einen neuen Server mit frischer Testdatenbank. Der Listenreporter ersetzt keine vollständigen Nachweise; danach `tools/verify_browser.py` für alle zwölf Ausführungen verwenden. Die zusätzlich gesicherten Einzellaufberichte heißen output/tests/e06-desktop-alone.xml und e06-mobile-alone.xml; e06-before.xml dokumentiert den davor reproduzierten Fehler.

benchmark.py misst nach fünf Aufwärmläufen 100 Testclient-Abfragen bei 1.000 Buchungen in zehn Räumen, einschließlich JSON-Dekodierung. Ziel: empirisches 95. Perzentil unter 250 ms. Dies ist keine Browser-, Netz- oder Dauerlastmessung.

Frontend lesbar halten: npm run format:frontend. Das formatiert nur HTML, CSS und JavaScript. Danach relevante Prüfungen erneut ausführen.

## Portfolio neu erzeugen

Nach passenden Änderungen Python- und Browsertests erneut ausführen. Der PDF-Bau lehnt Ergebnisse eines anderen Quellstands ab.

```powershell
.\.venv\Scripts\python.exe tools\build_portfolio.py
.\.venv\Scripts\python.exe tools\check_portfolio.py
```

Inhalt: docs/portfolio_inhalt.json; Metadaten: docs/portfolio_meta.json. Der Generator schreibt zusätzlich docs/portfolio.md. PDF: output/portfolio/Portfolio_Justin_Kolar_Raumzeit.pdf. Schriftwahl: Arial unter Windows, andernfalls die mit ReportLab gelieferte Vera-Familie. Paketversionen und Eingabeprüfsummen werden dokumentiert. Die PDF-Prüfung rendert ohne separate Poppler-Installation mit pypdfium2 und prüft Seitenzuordnung und Ränder.

Die gerenderten Seiten unter output/qa/pdf-current müssen tatsächlich visuell geprüft werden. Erst danach die Bestätigung mit tools/check_portfolio.py --confirm-visual-review --reviewer Name protokollieren. Für die vorliegende Ausgabe ist die prüfende Instanz als KI-Assistent bezeichnet; daraus entsteht kein persönlicher Nachweis.

```powershell
.\.venv\Scripts\python.exe tools\package_project.py
```

Das Archiv enthält Code, Dokumentation, aktuelle Ergebnisse und Screenshots, aber keine Laufzeitdaten oder Installationen. Der bisherige Stand vom 19.10. bleibt lokal unter output/history/2026-10-19 erhalten und wird nicht erneut ins aktuelle Archiv aufgenommen. review-before.xml belegt die zwei am 29.10. zunächst fehlgeschlagenen Regressionen; iteration-01.xml gehört zum älteren Verbesserungszyklus.

## Persönliche Prüfung und Abgabestand

Die tatsächlichen Rückmeldungen sind in docs/pruefung_ergebnisse.md und docs/persoenliche_ergebnisse.json dokumentiert. Die persönlich geprüfte, überarbeitete und freigegebene Reflexion liegt in docs/persoenliche_reflexion.md und wird im Portfolio unverändert übernommen. Die zusätzliche persönliche Code-Durchsicht wurde ausgelassen und bleibt als Grenze dokumentiert. Der vom Studierenden selbst gestartete 118-Test-Lauf einschließlich Screenshot und Rohberichten ist separat unter docs/nachweise/P5_Nutzerlauf_2026-10-29 erhalten. Er wird durch neue KI-gestützte Abschlussläufe nicht überschrieben. Die ursprüngliche Prüfanleitung steht in docs/eigene_pruefung.md; der Kolloquiumsleitfaden in docs/kolloquium.md.

Der Abgleich der verfügbaren Vorgaben und die daraus nicht belegten Informationen stehen in docs/abgabecheck.md. Finale Dateien: output/portfolio/Portfolio_Justin_Kolar_Raumzeit.pdf und output/dist/Raumzeit_Projekt.zip; Prüfsummen: output/dist/Pruefsummen.json. Vor der tatsächlichen Einreichung bleiben die nicht vorliegenden aktuellen Moodle-Vorgaben, Abgabeweg und genaue Uhrzeit zu prüfen. Es wurde nichts eingereicht oder versandt.

## Originalchat-Exporte für das Kolloquium

Die am 05.11.2026 nachgereichten [Originaldialoge stehen unter docs/originalchat/](docs/originalchat/README.md): der ursprüngliche Umsetzungschat **SE Chat** sowie der ergänzende Review-Chat **SE Prompt Chat**. Beide liegen als lesbare Markdown-Datei und strukturierte JSON-Datei mit Zeitangaben vor. Die ursprünglichen Bildanlagen und die tatsächlichen Fragebogenantworten sind enthalten. Umfang, Format und SHA-256-Prüfsummen sind im Exportverzeichnis dokumentiert. Interne Systemanweisungen und Denkprotokolle gehören nicht zum Dialogexport.

Die Exporte ergänzen den damaligen Abgabestand. Die bereits erstellte Portfolio-PDF und ihre historischen Prüfnachweise bleiben unverändert.
