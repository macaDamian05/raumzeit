# Architekturentscheidungen

## ADR 01 Lokaler modularer Monolith

Status: angenommen, 19.10.2026.

Kontext: Eine einzelne Person muss eine überschaubare Anwendung demonstrieren, prüfen und auf 10–15 Seiten erläutern können. Eine verteilte Bereitstellung wird nicht gefordert.

Entscheidung: Python mit Flask, lokales HTML/CSS/JavaScript und SQLite. Ein Prozess wird an 127.0.0.1 gebunden; Assets und Datenspeicherung benötigen im laufenden Betrieb keinen externen Dienst. Die fachlichen Module importieren weder Flask noch SQLite.

Alternativen: Django bietet bereits umfangreiche Benutzer- und Verwaltungsfunktionen, die hier außerhalb des Umfangs liegen. FastAPI wäre für eine getrennte API-Anwendung geeignet; für das lokale HTML-Frontend wäre zusätzlicher Aufbau erforderlich. Microservices und Cloudbetrieb würden Verteilung und Betrieb hinzufügen, ohne einen nachgewiesenen Bedarf zu erfüllen.

Konsequenzen: Einfache Vorführung, geringe Infrastruktur und verständliche Abhängigkeiten. Lokaler Einzelarbeitsplatz ohne Rollen und Benutzeridentität; Flask-Entwicklungsserver ist für die lokale Demonstration vorgesehen. Für einen Netzbetrieb wäre ein eigener Entwurf für Identität, Berechtigungen und Bereitstellung erforderlich.

## ADR 02 Atomare Konfliktprüfung und halboffene Zeitintervalle

Status: angenommen, 19.10.2026.

Kontext: Eine Prüfung nur im Browser oder ein Lesen vor Beginn der Schreibtransaktion verhindert keine konkurrierenden Doppelbuchungen.

Entscheidung: Alle fachlichen Änderungen beginnen eine SQLite-Transaktion mit BEGIN IMMEDIATE. Innerhalb dieser Transaktion werden Raum, Kapazität und mögliche Überschneidungen geprüft und anschließend gespeichert. Ein Fehler löst ROLLBACK aus. Eine aktive Buchung kollidiert genau dann, wenn bestehender_start < neues_ende UND bestehendes_ende > neuer_start. Stornierungen werden bei dieser Prüfung ignoriert; bei Änderungen wird die eigene ID ausgeschlossen.

Alternativen: Frontendprüfung alleine ist umgehbar. Ein einfacher UNIQUE-Index auf Raum und Startzeit erkennt Teilüberschneidungen nicht. Eine externe Datenbank mit Intervall-Constraints wäre möglich, ist für die lokale Anwendung aber zusätzlicher Betrieb.

Konsequenzen: Angrenzende Termine sind erlaubt. Konkurrierende Schreibvorgänge werden serialisiert; gleichzeitige Abfragen sind durch Integrationstests mit unabhängigen Verbindungen geprüft. Der getestete Fall ist kein allgemeiner Lastnachweis für beliebig viele Benutzer.

## ADR 03 Fachliche Schnittstellen und Unit of Work

Status: angenommen, 19.10.2026.

Kontext: Fachliche Regeln sollen unabhängig von HTTP und Datenbanksyntax nachvollziehbar bleiben; die Konsistenzprüfung benötigt jedoch eine gemeinsame Transaktion.

Entscheidung: Datenklassen und Eingaberegeln liegen in der Domäne. PlannerService koordiniert Anwendungsfälle über schmale Repository-Protokolle und eine injizierte UnitOfWorkFactory. Der SQLite-Adapter übernimmt Abfragen, Commit und Rollback. Die Application Factory setzt die Teile zusammen.

Alternativen: SQL direkt in den HTTP-Routen wäre kürzer, würde aber Verantwortlichkeiten und Prüfungen vermischen. Ein universelles CRUD-Repository würde unnötige Methoden und schlecht sichtbare Fachoperationen einführen.

Konsequenzen: SRP, ISP und DIP sind konkret an der Struktur erkennbar. OCP und LSP werden durch die Adapterverträge unterstützt, aber nicht als vollständig nachgewiesene Austauschbarkeit dargestellt: Ein zweiter vollständiger Datenbankadapter und statische Typprüfung sind nicht Bestandteil dieses Projekts.

## ADR 04 Stornierung und Versionsprüfung

Status: angenommen, 19.10.2026.

Kontext: Termine sollen nach einer Stornierung nicht mehr blockieren, aber weiterhin nachvollziehbar sein. Zwei geöffnete Browserdialoge können auf demselben veralteten Stand beruhen.

Entscheidung: Buchungen haben den Status active oder cancelled sowie eine positive Version. Änderungen und Stornierungen senden die zuvor gelesene Version. Eine abweichende Version wird innerhalb der Schreibtransaktion als Konflikt mit HTTP 409 abgewiesen. Jede erfolgreiche Status- oder Inhaltsänderung erhöht die Version. Eine erneute Stornierung mit aktueller Version ändert nichts.

Konsequenzen: Historie und verlorene Änderungen sind abgedeckt. Das ist kein vollständiges Auditlog: Frühere Inhalte und verantwortliche Benutzer werden nicht unveränderlich archiviert. Am 29.10.2026 auf Räume erweitert: Raumänderungen senden ebenfalls die gelesene Version. Serviceprüfung innerhalb der Transaktion und zusätzlich UPDATE WHERE id=? AND version=? verhindern ein Überschreiben. Die spätere Erweiterung wird nicht auf den ursprünglichen Entscheidungszeitpunkt zurückdatiert.


## ADR 05 Additive Datenbankmigration

Status: angenommen durch KI-gestützte Überarbeitung, 29.10.2026.

Kontext: Vorhandene Dateien aus Version 1.0 haben keine Raumversion. Eine Neuerstellung würde Bestandsdaten verlieren; ein optionales version-Feld bei Änderungen würde den Schutz umgehen.

Entscheidung: Schema-Version 2 ergänzt rooms.version als INTEGER NOT NULL DEFAULT 1 CHECK(version >= 1). Initialisierung und Migration laufen in einer gemeinsamen Schreibtransaktion. Bereits migrierte Felder werden nicht neu gesetzt. Unbekannte neuere Schema-Versionen werden mit Rollback zurückgewiesen. Raum- und Buchungsinhalte bleiben erhalten.

Konsequenzen: Alte Datenbankdateien sind mit Anwendung 1.1 weiter nutzbar. PUT /api/rooms/{id} verlangt nun die beim Lesen erhaltene positive Versionsnummer; fehlende Version liefert 422, veraltete 409. Ein Downgrade auf den alten Anwendungscode wird nicht unterstützt. Tests prüfen synthetischen Altbestand und wiederholte Initialisierung; zusätzlich werden Kopien vorhandener Dateien geprüft, nicht die Originale verändert.

## ADR 06 CSRF-Formatprüfung und Browserregressionen

Status: angenommen durch KI-gestützte Überarbeitung, 29.10.2026.

Kontext: 88 bestandene Python-Tests erfassten weder nicht-ASCII-haltige Token noch alle UI-Verarbeitungswege. compare_digest akzeptiert bei str nur ASCII; ein fremdes Headerzeichen führte zu TypeError. Ein 15-Minuten-Kalendereintrag bot für mehrere Textzeilen zu wenig Platz.

Entscheidung: Ungültige Tokenformate werden vor compare_digest mit 403 abgewiesen; gültige Token werden weiterhin verglichen. Sechs Playwright-Szenarien werden mit realem Testserver und echter Testdatenbank bei Desktop- und Mobilgröße wiederholt. Der Browser-Datumswert ist auf den 26.10.2026 fixiert; Timer, Netzwerk und Fachlogik bleiben aktiv. Ein kurzer Termin zeigt eine Titelzeile, vollständige Zeitangaben bleiben über zugänglichen Namen und Tooltip erhalten.

Konsequenzen: Python-Abdeckung, echte Browserassertionen und Sichtprüfung bleiben getrennte Nachweise. Screenshots dienen als zusätzliche Darstellung, nicht als Ersatz für Assertions. Chromium in zwei Viewports ist keine vollständige Browser-, Screenreader- oder WCAG-Prüfung.
