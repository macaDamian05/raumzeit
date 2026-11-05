"""Abgabearchiv ohne virtuelle Umgebung, Laufzeitdaten und Sitzungsschlüssel."""

from datetime import datetime,timezone
from pathlib import Path
import hashlib
import json
import os
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    from build_portfolio import check_source_manifest
    check_source_manifest()
    pdf=ROOT/"output/portfolio/Portfolio_Justin_Kolar_Raumzeit.pdf"
    qa=json.loads((ROOT/"output/tests/document_qa.json").read_text(encoding="utf-8"))
    assert qa["pdf_sha256"] == hashlib.sha256(pdf.read_bytes()).hexdigest()
    assert qa["main_text_pages"] == 12 and qa["all_rendered_pages_visually_reviewed"]
    assert qa["approved_reflection_text_verified"]
    build=json.loads((ROOT/"output/portfolio/build_manifest.json").read_text(encoding="utf-8"))
    for item in build["inputs"]:
        assert hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest()==item["sha256"],f'Dokumentquelle seit PDF-Bau verändert: {item["path"]}'
    target=ROOT/"output/dist/Raumzeit_Projekt.zip"
    target.parent.mkdir(parents=True,exist_ok=True)
    excluded={".venv",".git","__pycache__",".pytest_cache","instance","node_modules"}
    paths=[]
    for current, directories, filenames in os.walk(ROOT):
        relative=Path(current).relative_to(ROOT)
        directories[:]=[name for name in directories if name not in excluded]
        if relative==Path("output"):
            directories[:]=[name for name in directories if name not in {"qa","dist","history","coverage-html","screenshots"} and not name.startswith("test-temp")]
        if relative==Path("output/playwright"):
            directories[:]=[name for name in directories if name not in {"artifacts","html-report"}]
        for filename in filenames:
            path=Path(current)/filename
            if path.name==".coverage" or path.suffix in {".pyc",".secret",".db",".sqlite3",".wal",".shm"}:continue
            paths.append(path)
    paths.sort()
    with zipfile.ZipFile(target,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path in paths:archive.write(path,"Raumplaner/"+path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        names=archive.namelist()
        assert all(not any(part in excluded for part in Path(name).parts) for name in names)
        assert "Raumplaner/output/portfolio/Portfolio_Justin_Kolar_Raumzeit.pdf" in names
        assert "Raumplaner/output/tests/junit.xml" in names
        assert "Raumplaner/output/playwright/junit.xml" in names
        assert "Raumplaner/requirements-portfolio.txt" in names
        assert "Raumplaner/docs/persoenliche_reflexion.md" in names
        assert "Raumplaner/docs/pruefung_ergebnisse.md" in names
        assert "Raumplaner/docs/nachweise/P5_Nutzerlauf_2026-10-29/junit.xml" in names
        assert not any(name.startswith("Raumplaner/output/history/") for name in names)
    summary=dict(created_utc=datetime.now(timezone.utc).isoformat(),archive=target.name,files=len(paths),bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),pdf_sha256=qa["pdf_sha256"],archive_crc_verified=True)
    (target.parent/"Pruefsummen.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":main()
