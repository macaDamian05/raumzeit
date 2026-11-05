# Übermittelte Arbeitsanweisung vom 29.10.2026

Quelle: Nutzernachricht in diesem Chat. Die Bewertung ist als vom Nutzer übermittelte Einschätzung dokumentiert, nicht als zusätzlich verifizierte Dozentenkommunikation.

> Bitte überarbeite das Projekt „Raumzeit“ unter
> D:\Uni und Arbeit\Software Engineering\Raumplaner
> anhand der folgenden unabhängigen Bewertung aus Dozentensicht.
>
> Die Einschätzung war: technisch etwa 1,7–2,0, als derzeitige Einzelportfolio-Arbeitsfassung etwa 2,3. Die vorhandenen 88 Tests bestanden. Hauptverbesserungspunkte sind zwei nachgewiesene Fehler, die Absicherung des Frontends sowie die persönliche Prüfung und Reflexion.
>
> Bitte prüfe die Befunde zunächst selbst und setze die technischen und dokumentarischen Verbesserungen anschließend um:
>
> 1. CSRF-Fehler beheben:
> Ein ungültiges X-CSRF-Token mit Nicht-ASCII-Zeichen, beispielsweise „ä“, verursacht bei secrets.compare_digest einen TypeError und HTTP 500. Solche Eingaben müssen kontrolliert mit HTTP 403 abgelehnt werden. Ergänze einen Regressionstest; gültige Token müssen weiterhin funktionieren.
>
> 2. Verlorene Raumänderungen verhindern:
> Buchungen besitzen bereits einen Versionsschutz, Räume bisher nicht. Ein älterer Raumdialog kann neuere Änderungen überschreiben. Ergänze einen entsprechenden Schutz durch Datenhaltung, Service, API und Oberfläche. Bestehende Datenbanken müssen weiter verwendbar bleiben. Teste insbesondere, dass eine veraltete Änderung mit 409 abgewiesen wird und der aktuelle Datensatz erhalten bleibt.
>
> 3. Frontend verlässlich prüfen:
> Ergänze wenige wiederholbare Browsertests für Buchung anlegen, Überschneidung ablehnen, Buchung bearbeiten und stornieren. Prüfe außerdem mobile Bedienung und kurze 15-Minuten-Termine. Trenne Python-Abdeckung und Browsernachweise weiterhin klar.
>
> 4. Wartbarkeit und Reproduzierbarkeit verbessern:
> Formatiere das stark verdichtete HTML, CSS und JavaScript lesbar, ohne unnötigen Architekturumbau. Dokumentiere und fixiere die zusätzlichen Abhängigkeiten für die Portfolioerstellung, insbesondere ReportLab und Pillow.
>
> 5. Portfolio gezielt schärfen:
> Verknüpfe Anforderungen, Entscheidungen, Tests und Ergebnisse anhand konkreter Beispiele. Kürze Wiederholungen und aktualisiere die tatsächlich ausgeführten Prüfungen und bekannten Grenzen. Berücksichtige die dokumentierte Bewertungsmatrix mit 20 % Projektmanagement, 50 % Inhalt, 20 % Struktur/Argumentation und 10 % Formales.
>
> Wichtig: Erfinde keine persönlichen Tätigkeiten, Lernerfahrungen, Betreuerkommunikation oder Eigenständigkeitsnachweise von mir. Kennzeichne deine Prüfungen als KI-gestützt. Bereite die persönliche Prüfung vor und leite mich anschließend durch konkrete Aufgaben und Reflexionsfragen. Trage persönliche Ergebnisse erst nach meiner tatsächlichen Durchführung und Rückmeldung ein.
>
> Halte den bestehenden lokalen Funktionsumfang ein. Neue Cloud-, Login- oder Serienfunktionen sind nicht erforderlich.
>
> Führe die relevanten Prüfungen aus, aktualisiere anschließend Portfolio, Testnachweise und Abgabearchiv konsistent und prüfe das PDF visuell. Berichte abschließend knapp, was verbessert wurde, welche Prüfungen bestanden haben und welche persönlichen Schritte vor der Abgabe noch offen sind.
