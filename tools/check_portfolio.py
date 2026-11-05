"""PDF strukturell prüfen und rendern; Sichtprüfung separat bestätigen."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import pdfplumber
import pypdfium2 as pdfium
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "output/portfolio/Portfolio_Justin_Kolar_Raumzeit.pdf"
TARGET = ROOT / "output/tests/document_qa.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm-visual-review", action="store_true")
    parser.add_argument("--reviewer")
    args = parser.parse_args()
    digest = hashlib.sha256(PDF.read_bytes()).hexdigest()
    if args.confirm_visual_review:
        if not args.reviewer:
            parser.error("Die tatsächliche prüfende Person beziehungsweise KI muss benannt werden.")
        record = json.loads(TARGET.read_text(encoding="utf-8"))
        assert record["pdf_sha256"] == digest, "PDF seit dem Rendern verändert."
        assert all((ROOT / item).is_file() for item in record["rendered_pages"])
        record.update(all_rendered_pages_visually_reviewed=True, visual_reviewer=args.reviewer,
                      visual_review_utc=datetime.now(timezone.utc).isoformat())
        TARGET.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Tatsächlich erfolgte Sichtprüfung protokolliert.")
        return
    reader = PdfReader(PDF)
    chapters = json.loads((ROOT / "docs/portfolio_inhalt.json").read_text(encoding="utf-8"))
    for index, chapter in enumerate(chapters, 2):
        assert chapter["title"] in reader.pages[index].extract_text(), (index + 1, chapter["title"])
    assert "Literatur und Quellenverzeichnis" in reader.pages[14].extract_text()
    assert "Anhang A" in reader.pages[15].extract_text()
    personal = json.loads((ROOT / "docs/persoenliche_ergebnisse.json").read_text(encoding="utf-8"))
    approved = personal["reflexion"]
    reflection_path = ROOT / approved["path"]
    assert personal["fachliche_freigabe"] and approved["persoenlich_freigegeben"]
    assert hashlib.sha256(reflection_path.read_bytes()).hexdigest() == approved["file_sha256"]
    reflection = reflection_path.read_text(encoding="utf-8")
    body, limits = reflection.split("## Freigegebene Reflexion", 1)[1].split("## Nachweisgrundlage und Grenzen", 1)
    pdf_text = "".join("".join((page.extract_text() or "").split()) for page in reader.pages)
    for paragraph in (body + "\n\n" + limits).split("\n\n"):
        if paragraph.strip():
            assert "".join(paragraph.split()) in pdf_text, "Freigegebener Text nicht vollständig im PDF."
    assert "Abgabefassung" in reader.pages[0].extract_text()
    issues = []
    with pdfplumber.open(PDF) as document:
        for number, page in enumerate(document.pages, 1):
            for word in page.extract_words():
                if word["x0"] < 45 or word["x1"] > page.width - 42:
                    issues.append({"page": number, "word": word["text"]})
    assert not issues, issues
    folder = ROOT / "output/qa/pdf-current"
    folder.mkdir(parents=True, exist_ok=True)
    rendered = []
    with pdfium.PdfDocument(PDF) as document:
        for index in range(len(document)):
            page = document[index]
            bitmap = page.render(scale=1.7)
            target = folder / f"page-{index + 1:02d}.png"
            bitmap.to_pil().save(target)
            rendered.append(target.relative_to(ROOT).as_posix())
            bitmap.close()
            page.close()
    record = dict(pdf_pages=len(reader.pages), main_text_pages=12, pre_appendix_pages=15,
                  appendix_start=16, margin_issue_count=0, chapter_pagination_verified=True,
                  approved_reflection_text_verified=True, approved_reflection_sha256=approved["file_sha256"],
                  all_rendered_pages_visually_reviewed=False, pdf_sha256=digest,
                  rendered_pages=rendered, rendered_utc=datetime.now(timezone.utc).isoformat())
    TARGET.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"{len(reader.pages)} Seiten gerendert. Sichtprüfung ist noch offen: {folder}")


if __name__ == "__main__":
    main()
