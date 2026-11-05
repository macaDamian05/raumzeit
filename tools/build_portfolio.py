"""Erstellt PDF und Markdown aus Inhalten und tatsächlich vorliegenden Nachweisen."""

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import importlib.metadata
import json
import platform
import re
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, Flowable, KeepTogether

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/"output"/"portfolio"
WIDTH=A4[0]-120
FONTDIR=Path("C:/Windows/Fonts")
font_files=[("Arial","arial.ttf"),("Arial-Bold","arialbd.ttf"),("Arial-Italic","ariali.ttf")]
if not (FONTDIR/"arial.ttf").is_file():
    import reportlab
    FONTDIR=Path(reportlab.__file__).parent/"fonts"
    font_files=[("Arial","Vera.ttf"),("Arial-Bold","VeraBd.ttf"),("Arial-Italic","VeraIt.ttf")]
for name,file in font_files:
    pdfmetrics.registerFont(TTFont(name,str(FONTDIR/file)))
pdfmetrics.registerFontFamily("Arial",normal="Arial",bold="Arial-Bold",italic="Arial-Italic",boldItalic="Arial-Bold")
STYLES={
 "body":ParagraphStyle("body",fontName="Arial",fontSize=10.5,leading=14.5,spaceAfter=8,alignment=TA_JUSTIFY,textColor=colors.HexColor("#17212e")),
 "heading":ParagraphStyle("heading",fontName="Arial-Bold",fontSize=16,leading=21,spaceAfter=15,textColor=colors.black),
 "sub":ParagraphStyle("sub",fontName="Arial-Bold",fontSize=11.5,leading=16,spaceBefore=9,spaceAfter=8),
 "small":ParagraphStyle("small",fontName="Arial",fontSize=8.7,leading=12,spaceAfter=7),
 "cell":ParagraphStyle("cell",fontName="Arial",fontSize=8.5,leading=11.5),
 "header":ParagraphStyle("header",fontName="Arial-Bold",fontSize=8.5,leading=11.5,textColor=colors.white),
 "caption":ParagraphStyle("caption",fontName="Arial-Italic",fontSize=8,leading=11,textColor=colors.HexColor("#5d6673"),spaceBefore=5,spaceAfter=12),
 "code":ParagraphStyle("code",fontName="Courier",fontSize=8,leading=12,spaceBefore=4,spaceAfter=12),
 "cover":ParagraphStyle("cover",fontName="Arial-Bold",fontSize=28,leading=35,spaceAfter=20,textColor=colors.black),
 "cover_sub":ParagraphStyle("cover_sub",fontName="Arial",fontSize=15,leading=22,spaceAfter=26),
}


def load(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))


class Diagram(Flowable):
    def __init__(self,kind):
        super().__init__(); self.kind=kind; self.width=WIDTH; self.height={"intervals":132,"architecture":210,"data":135}[kind]

    def draw(self):
        c=self.canv; c.saveState();c.scale(WIDTH/486,1);c.setFont("Arial",8)
        def box(x,y,w,h,title,lines=(),fill="#f4f6f9"):
            c.setStrokeColor(colors.HexColor("#bdc7d4"));c.setFillColor(colors.HexColor(fill));c.roundRect(x,y,w,h,5,fill=1,stroke=1)
            c.setFillColor(colors.HexColor("#17212e"));c.setFont("Arial-Bold",9);c.drawCentredString(x+w/2,y+h-16,title)
            c.setFont("Arial",8)
            for i,line in enumerate(lines): c.drawCentredString(x+w/2,y+h-31-i*12,line)
        def arrow(x,y,a,b,label=""):
            c.setStrokeColor(colors.HexColor("#6c7e97"));c.setLineWidth(1);c.line(x,y,a,b)
            import math
            angle=math.atan2(b-y,a-x)
            c.line(a,b,a-6*math.cos(angle-.45),b-6*math.sin(angle-.45));c.line(a,b,a-6*math.cos(angle+.45),b-6*math.sin(angle+.45))
            if label:
                c.setFillColor(colors.HexColor("#516078"));c.setFont("Arial",7);c.drawCentredString((x+a)/2+30,(y+b)/2+3,label)
        if self.kind=="architecture":
            box(130,160,225,45,"Browser",["HTML / CSS / JavaScript"])
            box(130,95,225,47,"Webadapter und Application Factory",["HTTP / Sitzung / JSON / Zusammensetzung"])
            box(0,12,225,62,"PlannerService und Domäne",["Anwendungsfälle / Eingaberegeln","Verträge in ports.py"])
            box(261,12,225,62,"SQLite-Adapter",["Repositories / Unit of Work","Datenbankdatei auf lokalem Rechner"])
            arrow(242,160,242,143,"HTTP")
            arrow(180,95,120,75,"Aufruf")
            arrow(225,42,260,42)
            c.setFont("Arial",7.5);c.setFillColor(colors.HexColor("#52627b"));c.drawCentredString(WIDTH/2,0,"Laufzeit: Service -> Adapter. Quellcode: Service -> Vertrag; Adapter erfüllt Vertrag.")
        elif self.kind=="data":
            box(0,10,205,117,"rooms",["id (PK) / name / name_key (UNIQUE)","capacity / location","equipment / color / version"])
            box(270,10,216,117,"bookings",["id (PK) / room_id (FK)","title / organizer / participants","start / end / status / version"])
            arrow(205,65,269,65)
            c.setFont("Arial-Bold",8);c.drawString(214,76,"1 : n")
        else:
            c.setStrokeColor(colors.HexColor("#bdc7d4"));c.line(125,108,455,108)
            for x,label in [(125,"09:00"),(235,"09:30"),(345,"10:00"),(455,"10:30")]:
                c.setFillColor(colors.HexColor("#52627b"));c.setFont("Arial",8);c.drawCentredString(x,117,label)
            for y,start,end,label,fill in [(80,125,345,"Bestehende Buchung", "#dce8fa"),(49,290,455,"Konflikt", "#f4dddd"),(18,345,455,"Anschluss erlaubt", "#dceee7")]:
                c.setFillColor(colors.HexColor(fill));c.setStrokeColor(colors.HexColor("#9baac0"));c.roundRect(start,y,end-start,22,3,fill=1)
                c.setFillColor(colors.HexColor("#24354d"));c.setFont("Arial",8);c.drawString(0,y+7,label)
        c.restoreState()


class Portfolio:
    def __init__(self):
        self.story=[];self.markdown=[];self.figures=[];self.tables=[]
        self.main=load("docs/portfolio_inhalt.json");self.requirements=load("docs/anforderungen.json");self.sources=load("docs/quellen.json")
        self.meta=load("docs/portfolio_meta.json")
        self.personal=load("docs/persoenliche_ergebnisse.json")
        assert self.personal.get("fachliche_freigabe") and self.personal.get("pruefung_abgeschlossen"),"Persönliche Freigabe fehlt."
        approved=self.personal["reflexion"]
        assert approved["persoenlich_freigegeben"]
        assert hashlib.sha256((ROOT/approved["path"]).read_bytes()).hexdigest()==approved["file_sha256"],"Freigegebene Reflexion nachträglich verändert."
        self.coverage=load("output/tests/coverage.json")["totals"]
        self.env=load("output/tests/environment.json");self.bench=load("output/tests/benchmark.json");self.browser=load("output/tests/browser.json")
        suites=ET.parse(ROOT/"output/tests/junit.xml").getroot()
        self.cases=suites.findall(".//testcase"); self.groups=Counter(case.attrib["classname"].split(".")[-1] for case in self.cases)
        assert all(case.find("failure") is None and case.find("error") is None for case in self.cases),"Keine fehlgeschlagenen Testergebnisse als Erfolg dokumentieren"
        assert all(row["passed"] for row in self.browser["scenarios"])
        expected_browser_ids={f"{project}-E{index:02d}" for project in ["desktop","mobile"] for index in range(1,7)}
        assert self.browser.get("status")=="passed" and len(self.browser["scenarios"])==12
        assert {case["id"] for case in self.browser["scenarios"]}==expected_browser_ids
        known_tests={case.attrib["name"].split("[")[0] for case in self.cases}
        browser_cases={case["id"].split("-")[-1] for case in self.browser["scenarios"]}
        for item in self.requirements:
            for evidence in item["evidence"]:
                if evidence.startswith("test_"):
                    assert evidence in known_tests,f"Unbelegter Testname: {evidence}"
                for case_id in re.findall(r"\bE\d{2}\b", evidence):
                    assert case_id in browser_cases,f"Unbelegter Browserfall: {case_id}"

    def p(self,text,style="body"):
        self.story.append(Paragraph(escape(str(text)).replace("\n","<br/>"),STYLES[style]));self.markdown.append(str(text)+"\n")

    def heading(self,title):
        self.story.append(Paragraph(escape(title),STYLES["heading"]));self.markdown.append("\n## "+title+"\n")

    def table(self,headers,rows,caption,widths=None):
        number=len(self.tables)+1;self.tables.append((number,caption))
        self.story.append(Paragraph(escape(f"Tabelle {number}: {caption}"),STYLES["caption"]))
        data=[[Paragraph(escape(str(x)),STYLES["header"]) for x in headers]]
        data += [[Paragraph(escape(str(x)).replace("\n","<br/>"),STYLES["cell"]) for x in row] for row in rows]
        columns=[WIDTH*x for x in widths] if widths else [WIDTH/len(headers)]*len(headers)
        table=Table(data,colWidths=columns,repeatRows=1,hAlign="LEFT")
        table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#34445a")),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f3f5f8")]),("GRID",(0,0),(-1,-1),.4,colors.HexColor("#d9d9d9")),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
        self.story.extend([table,Spacer(1,12)])
        self.markdown.extend([f"**Tabelle {number}: {caption}**\n","| "+" | ".join(headers)+" |","| "+" | ".join("---" for _ in headers)+" |"]+["| "+" | ".join(str(x).replace("\n"," ") for x in row)+" |" for row in rows]+["\n"])

    def caption(self,text):
        number=len(self.figures)+1;self.figures.append((number,text));self.p(f"Abbildung {number}: {text}","caption")

    def image(self,path,caption,max_height=300):
        image=Image(str(ROOT/path));ratio=min(WIDTH/image.imageWidth,max_height/image.imageHeight)
        image.drawWidth=image.imageWidth*ratio;image.drawHeight=image.imageHeight*ratio;image.hAlign="CENTER"
        self.story.append(image);self.caption(caption)

    def newpage(self): self.story.append(PageBreak())

    def block(self,block):
        kind=block["type"]
        if kind=="p": self.p(block["text"])
        elif kind=="table": self.table(block["headers"],block["rows"],block["caption"],block.get("widths"))
        elif kind=="diagram": self.story.append(Diagram(block["kind"]));self.caption(block["caption"])
        elif kind=="image": self.image(block["path"],block["caption"],block.get("max_height",300))
        elif kind=="code": self.p(block["text"],"code")
        elif kind=="test_groups":
            rows=[["Domäne",self.groups.get("test_domain",0),"Isolierte Eingaberegeln und Grenzwerte"],["Anwendungsfälle + SQLite",self.groups.get("test_application",0)+self.groups.get("test_room_versions",0),"Konsistenz, Versionen, Migration und Konkurrenz"],["HTTP-Adapter + Regressionen",self.groups.get("test_web",0)+self.groups.get("test_review_regressions",0),"Testclient, JSON, CSRF-Formate und Statuscodes"]]
            self.table(["Ebene","Fälle","Zweck"],rows,"Ausgeführte automatisierte Testfälle nach Ebene",[.29,.12,.59])
        elif kind=="test_summary":
            rows=[["Python-Testfälle",str(len(self.cases)),"Alle bestanden; keine übersprungenen Fälle"],["Python-Zeilen",f'{self.coverage["covered_lines"]} / {self.coverage["num_statements"]}',f'{self.coverage["percent_statements_covered"]:.2f} %'],["Python-Zweige",f'{self.coverage["covered_branches"]} / {self.coverage["num_branches"]}',f'{self.coverage["percent_branches_covered"]:.2f} %'],["Python-Abdeckung kombiniert",f'{self.coverage["percent_covered"]:.2f} %',"Keine Aussage zur JavaScript-Abdeckung"],["Browserausführungen",str(len(self.browser["scenarios"])),"Sechs Szenarien in zwei Viewports; alle bestanden"],["Umgebung",f'Python {self.env["python"]}',f'Flask {self.env["packages"]["Flask"]}; SQLite {self.env["sqlite"]}']]
            self.table(["Nachweis","Wert","Einordnung"],rows,"Tatsächlicher Verifikationsstand vom "+self.meta["stand"],[.31,.25,.44])
        elif kind=="benchmark":
            b=self.bench
            self.table(["Messgröße","Ergebnis"],[["Median",f'{b["median_ms"]} ms'],["Empirisches 95. Perzentil",f'{b["p95_ms"]} ms'],["Maximum",f'{b["max_ms"]} ms'],["Zielwert / Ergebnis",f'P95 < {b["target_p95_ms"]} ms / '+("erfüllt" if b["passed"] else "nicht erfüllt")]],"Lokale Adaptermessung mit 1.000 Buchungen",[.6,.4])

    def md_section(self,path):
        content=(ROOT/path).read_text(encoding="utf-8")
        # Markdown-Tabellen stehen im Originalprotokoll; der Anhang nutzt ihre Textzeilen.
        table_headers=None
        for line in content.splitlines():
            if not line.strip() or re.match(r"^\|[- :|]+\|$",line): continue
            if line.startswith("# "):continue
            if line.startswith("|"):
                values=[x.strip() for x in line.strip("|").split("|")]
                if table_headers is None:
                    table_headers=values
                else:
                    self.p(values[0],"sub")
                    for heading,value in zip(table_headers[1:],values[1:]):self.p(f"{heading}: {value}","small")
                continue
            if line.startswith("#"): self.p(line.lstrip("# "),"sub")
            else:self.p(line.replace("`", ""),"small")

    def build(self):
        OUTPUT.mkdir(parents=True,exist_ok=True)
        self.story.append(Spacer(1,54))
        self.p("Webbasiertes\nRaumbuchungssystem\nmit Python","cover")
        self.p("Konzeption, Implementierung und Qualitätssicherung","cover_sub")
        self.p("Portfolio zur Einzelabgabe im Modul Software Engineering","sub")
        self.story.append(Spacer(1,33))
        for text in ["Studierender: Justin Kolar","Betreuer: Sandro Hartenstein","Anwendung: Raumzeit "+self.meta["version"],"Stand: "+self.meta["stand_lang"],"Vorgesehene Abgabe: "+self.meta["abgabe"]]: self.p(text)
        self.story.append(Spacer(1,28))
        self.p(self.meta["status"]+" mit dokumentierter KI-Unterstützung","sub")
        self.p("Persönliche Funktionsprüfung und eigener Testlauf sind dokumentiert. Die Reflexion wurde KI-gestützt formuliert, von Justin Kolar persönlich geprüft, überarbeitet und am "+self.meta["persoenlich_freigegeben_am"]+" freigegeben. Der dokumentierte Prüfumfang bleibt maßgeblich.")
        self.p("Umfang: zwölf Seiten fachlicher Haupttext; Titelblatt, Verzeichnis und Quellenverzeichnis zusätzlich. Nachweise und Prompt-Log folgen im Anhang.","small")
        self.newpage();self.heading("Inhaltsverzeichnis")
        toc_rows=[[Paragraph(escape(page["title"]),STYLES["small"]),str(i)] for i,page in enumerate(self.main,3)]
        toc_rows.append([Paragraph("Literatur und Quellenverzeichnis",STYLES["small"]),"15"])
        toc=Table(toc_rows,colWidths=[WIDTH-30,30],hAlign="LEFT")
        toc.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),"Arial"),("FONTSIZE",(0,0),(-1,-1),9),("ALIGN",(1,0),(1,-1),"RIGHT"),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
        self.story.append(toc)
        self.story.append(Spacer(1,13));self.p("Anhang","sub")
        for text in ["A  Vollständige Anforderungen und Akzeptanzkriterien","B  KI-Protokoll mit Originalauszügen aus Nutzereingaben","C  Tatsächliche Browser- und Testnachweise","D  Persönliche Prüfergebnisse, Reflexion und Belege"]:self.p(text,"small")
        self.story.append(Spacer(1,15));self.p("Hinweise zur Nachvollziehbarkeit","sub")
        self.p("Die Kennungen F und N verbinden Anforderungen mit Python-Testnamen und den Browserfällen E01 bis E06. Die sechs Browserfälle laufen jeweils im Desktop- und Mobilviewport. Verwendet wird die numerische Zitierweise [1] bis [13]. Quellenabrufe erfolgten am 19. und 29.10.2026.")
        self.p("Dateibelege: output/tests/ enthält die aktuellen maschinenlesbaren Ergebnisse. docs/ enthält Auftrag, Projektverlauf, ADRs, Quellen, KI-Protokoll und persönliche Prüfergebnisse. Der persönliche Testlauf bleibt unter docs/nachweise separat erhalten. Quellstand und freigegebene Reflexion sind mit SHA-256-Prüfsummen abgesichert.")
        for page in self.main:
            self.newpage();self.heading(page["title"])
            for block in page["blocks"]:self.block(block)
        self.newpage();self.heading("Literatur und Quellenverzeichnis")
        for source in self.sources:
            text=f'[{source["id"]}] {source["author"]} ({source["year"]}). {source["title"]}.'
            if source["url"]: text+=f' {source["url"]} (Zugriff: {source["accessed"]}).'
            else: text+=" Bereitgestellte Kursunterlagen im Ordner Folien PDF-20261019; Anforderungen, Folien 20–26; Architektur Basics, Folien 16–18."
            self.p(text,"small")
        self.p("Die bereitgestellten Unterlagen von 2025 werden für Fachkonzepte verwendet. Die Einzelabgabe 2026 richtet sich nach den im Chat übermittelten Vorgaben und der Bewertungsmatrix; diese Kommunikation ist Projektgrundlage und keine veröffentlichte Fachliteratur.","small")
        self.p("Abbildungen und Tabellen sind eigene Darstellungen des vorliegenden Projekts. Screenshots zeigen die tatsächlich ausgeführte Anwendung mit fiktiven Beispieldaten.","small")
        self.newpage();self.heading("Anhang A Anforderungen und Akzeptanzkriterien")
        self.p("Die folgende Spezifikation ist aus docs/anforderungen.json übernommen. Die als umgesetzt ausgewiesenen Anforderungen besitzen konkrete Kriterien und zugeordnete Nachweise. Could- und Won't-Einträge grenzen spätere Wünsche ab.","small")
        for item in self.requirements:
            start=len(self.story)
            self.story.extend([Paragraph(escape(f'{item["id"]} {item["title"]}'),STYLES["sub"]),Paragraph(escape(f'Priorität: {item["priority"]} | Stand: {item["status"]}'),STYLES["small"])])
            self.p(item["story"],"small")
            for index,criterion in enumerate(item["acceptance"],1): self.p(f'AK {index}: {criterion}',"small")
            if item["evidence"]:self.p("Nachweise: "+"; ".join(item["evidence"]),"small")
            self.story[start:]=[KeepTogether(self.story[start:])]
        self.newpage();self.heading("Anhang B Dokumentation der KI-Nutzung")
        self.md_section(Path("docs/ki_protokoll.md"))
        self.newpage();self.heading("Anhang C Ausgeführte Browser- und Testnachweise")
        self.p("KI-gestützt erstellte und ausgeführte Playwright-Tests mit echtem Chromium, Flask und SQLite. Dieser automatisierte Browsernachweis ist von der Python-Abdeckung und den persönlichen Kontrollen in Anhang D getrennt. Das Browserdatum ist auf den 26.10.2026 fixiert; die tatsächliche Ausführung erfolgte am "+self.meta["stand"]+".")
        purposes={
            "E01":"Raum und Buchung über die UI erstellen, nach Neuladen sichtbar; mobil Agenda ohne horizontalen Überlauf.",
            "E02":"Teilüberschneidung liefert 409 und sichtbare Meldung; vollständiger alter Datensatz bleibt erhalten.",
            "E03":"Änderung liefert Version 2; Stornierung Version 3 und Historieneintrag, dieser Termin ist nicht mehr aktiv.",
            "E04":"15-Minuten-Titel ohne vertikales Abschneiden; Tastatur öffnet Dialog mit den richtigen Zeiten.",
            "E05":"Zwei Raumdialoge mit Version 1: erster speichert Version 2, zweiter erhält 409; aktueller Datensatz unverändert.",
            "E06":"Wochenwechsel/Heute, Raumfilter sowie Suche nach Titel und Person einschließlich Leerzustand funktionieren."
        }
        for case_id,purpose in purposes.items():
            self.p(case_id+" "+purpose,"sub")
            matching=[row for row in self.browser["scenarios"] if row["id"].endswith(case_id)]
            self.p("Ist: "+"; ".join(f'{row["project"]}: {row["status"]} ({row["duration_ms"]} ms)' for row in matching),"small")
        self.p("Die Testdatei prüft außerdem auf unbehandelte JavaScript-Ausnahmen. Chromium in zwei Viewports ersetzt keine vollständige Browser- und Screenreadermatrix. Erwartungswerte sind Assertions, keine erfundenen persönlichen Beobachtungen.","small")
        self.newpage();self.heading("Anhang C Bildschirmnachweise")
        self.image("output/playwright/screenshots/desktop-E02.png","Zurückweisung einer Überschneidung im wiederholbaren Browserfall E02",245)
        self.image("output/playwright/screenshots/desktop-E05-Konflikt.png","Veralteter Raumdialog wird nach vorheriger Änderung mit 409 abgewiesen; Fall E05",245)
        self.newpage();self.heading("Anhang C Mobile Darstellung und Ergebnisdateien")
        self.image("output/playwright/screenshots/mobile-E01.png","Mobile Agenda im 390-Pixel-Viewport; Browserfall E01",340)
        self.p("Nachweisdateien","sub")
        for path in ["output/tests/junit.xml; coverage.json; environment.json","output/tests/review-before.xml (zwei reproduzierte Fehler)","output/tests/e06-before.xml; e06-desktop-alone.xml; e06-mobile-alone.xml","output/tests/benchmark.json; migration.json","output/playwright/junit.xml; results.json; screenshots/","output/tests/browser.json; source_manifest.json; browser_source_manifest.json"]: self.p(path,"small")
        self.p("JUnit und Coverage enthalten die aktuellen Python-Ergebnisse. Playwright besitzt einen eigenen Rohbericht und ein eigenes Quellmanifest. Ein erster Korrekturzyklus vom 19.10. ist historisch archiviert; seine Werte werden nicht als neuer Testlauf ausgegeben.","small")
        self.newpage();self.heading("Anhang D Persönliche Prüfergebnisse")
        self.md_section(Path("docs/pruefung_ergebnisse.md"))
        self.newpage();self.heading("Anhang D Persönliche Reflexion")
        self.md_section(Path("docs/persoenliche_reflexion.md"))
        self.newpage();self.heading("Anhang D Persönliche Nachweise")
        self.image("docs/nachweise/P1_Raumverwaltung_2026-10-29.png","Vom Studierenden bereitgestellter Screenshot der Raumverwaltung: Prüfraum Damian mit sechs Plätzen",220)
        self.image("docs/nachweise/P5_Nutzerlauf_2026-10-29/PowerShell_Testergebnis.png","Vom Studierenden gestarteter Python-Testlauf: 118 bestanden; Python-Abdeckung gerundet 99 Prozent",220)
        self.p("Diese Screenshots wurden vom Studierenden im Chat übermittelt. Der persönliche Python-Lauf bleibt einschließlich Rohberichten separat unter docs/nachweise/P5_Nutzerlauf_2026-10-29 erhalten. Die Browserbilder in Anhang C stammen aus den automatisierten KI-gestützten Prüfungen.","small")
        def page_frame(canvas,doc):
            canvas.saveState();canvas.setFillColor(colors.HexColor("#6d7581"));canvas.setFont("Arial",7.5)
            if doc.page>1:
                canvas.drawString(54,A4[1]-33,"Justin Kolar | Software Engineering | Raumzeit")
                canvas.setStrokeColor(colors.HexColor("#d9dfe8"));canvas.line(54,A4[1]-43,A4[0]-54,A4[1]-43)
            canvas.drawString(54,28,self.meta["status"]+" mit KI-Unterstützung | "+self.meta["stand"])
            canvas.drawRightString(A4[0]-54,28,str(doc.page));canvas.restoreState()
        target=OUTPUT/"Portfolio_Justin_Kolar_Raumzeit.pdf"
        document=SimpleDocTemplate(str(target),pagesize=A4,leftMargin=54,rightMargin=54,topMargin=62,bottomMargin=49,title="Raumzeit Raumbuchungssystem mit Python",author="Justin Kolar mit dokumentierter KI-Unterstützung")
        document.build(self.story,onFirstPage=page_frame,onLaterPages=page_frame)
        (ROOT/"docs"/"portfolio.md").write_text("# Raumzeit Portfolio\n\n"+"\n".join(self.markdown),encoding="utf-8")
        inputs=[path for path in (ROOT/"docs").rglob("*") if path.is_file() and path.name!="portfolio.md"]
        inputs.extend(ROOT/"output/tests"/name for name in ["junit.xml","coverage.json","environment.json","benchmark.json","migration.json","browser.json","source_manifest.json","browser_source_manifest.json","e06-before.xml","e06-desktop-alone.xml","e06-mobile-alone.xml"])
        inputs.extend(ROOT/"output/playwright"/name for name in ["junit.xml","results.json"])
        inputs.extend((ROOT/"output/playwright/screenshots").glob("*.png"))
        environment={"built_utc":datetime.now(timezone.utc).isoformat(),"python":platform.python_version(),
                     "packages":{name:importlib.metadata.version(name) for name in ["reportlab","Pillow","pypdf","pdfplumber","pypdfium2"]},
                     "font_files":[file for _,file in font_files],"approved_reflection_sha256":self.personal["reflexion"]["file_sha256"],
                     "inputs":[{"path":path.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()} for path in sorted(inputs)]}
        (OUTPUT/"build_manifest.json").write_text(json.dumps(environment,ensure_ascii=False,indent=2),encoding="utf-8")
        print(target)


def check_source_manifest():
    manifest=load("output/tests/source_manifest.json")
    assert "verified_utc" in manifest,"Bitte tools/verify.py für einen geprüften Quellstand ausführen."
    from verify import source_files
    assert source_files()==manifest["files"],"Quellstand verändert; bitte tools/verify.py erneut ausführen."
    for item in manifest["files"]:
        assert hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest()==item["sha256"],f'Quellstand verändert: {item["path"]}. Tests erneut ausführen.'
    browser_manifest=load("output/tests/browser_source_manifest.json")
    assert browser_manifest["files"]==manifest["files"],"Python- und Browserergebnisse gehören nicht zum selben Quellstand."


def check_document_dependencies():
    for line in (ROOT/"requirements-portfolio.txt").read_text(encoding="utf-8").splitlines():
        line=line.strip()
        if not line or line.startswith("#"):continue
        name,version=line.split("==",1)
        assert importlib.metadata.version(name)==version,f'Abhängigkeit {name}: bitte requirements-portfolio.txt installieren.'


if __name__=="__main__":
    check_document_dependencies();check_source_manifest();Portfolio().build()
