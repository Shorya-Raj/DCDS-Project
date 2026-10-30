"""Offline checks for the public collection scripts; no portal requests are made."""

import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "skills" / "mahatenders-extract" / "scripts"
SCRATCH_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


manifest_script = load_script("make_manifest")
capture_script = load_script("capture_tenders")


class FakePage:
    def __init__(self, results):
        self.results = iter(results)
        self.visits = []

    def goto(self, url, **_kwargs):
        self.visits.append(url)

    def wait_for_function(self, *_args, **_kwargs):
        return None

    def evaluate(self, _code, _metadata):
        return next(self.results)


class ExtractionTests(unittest.TestCase):
    def test_manifest_starts_after_marker_and_keeps_duplicate_positions(self):
        # This tiny document exercises real DOCX hyperlink relationships.
        document_xml = """<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>
          <w:p><w:hyperlink r:id="r1"><w:r><w:t>old</w:t></w:r></w:hyperlink></w:p>
          <w:p><w:r><w:t>NEW ↓</w:t></w:r></w:p>
          <w:p><w:r><w:t>ELECTRICAL WORKS</w:t></w:r></w:p>
          <w:p><w:hyperlink r:id="r2"><w:r><w:t>first</w:t></w:r></w:hyperlink></w:p>
          <w:p><w:hyperlink r:id="r2"><w:r><w:t>repeat</w:t></w:r></w:hyperlink></w:p>
          </w:body></w:document>"""
        relationships_xml = """<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
          <Relationship Id="r1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"
            Target="https://mahatenders.gov.in/old" TargetMode="External"/>
          <Relationship Id="r2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"
            Target="https://mahatenders.gov.in/nicgep/app?example=1" TargetMode="External"/>
          </Relationships>"""
        SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=SCRATCH_DIR) as temporary:
            path = Path(temporary) / "links.docx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", document_xml)
                archive.writestr("word/_rels/document.xml.rels", relationships_xml)
            _marker, occurrences, rows = manifest_script.build_manifest(path, "NEW", None)
        self.assertEqual(occurrences, 2)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["categories"], ["ELECTRICAL WORKS"])
        self.assertEqual(len(rows[0]["paragraphs"]), 2)

    def test_capture_resumes_and_retries_only_the_exact_link(self):
        url = "https://mahatenders.gov.in/nicgep/app?example=1"
        page = FakePage([{"status": "unavailable"}, {"status": "captured", "fields": {"Tender ID": "TEST_1"}}])
        result = capture_script.read_page(page, {"url": url, "categories": []}, "extractor")
        self.assertEqual(result["status"], "captured")
        self.assertEqual(page.visits, [url, capture_script.PORTAL_HOME, url])

    def test_captcha_stops_before_retry(self):
        url = "https://mahatenders.gov.in/nicgep/app?example=2"
        page = FakePage([{"status": "captcha"}])
        result = capture_script.read_page(page, {"url": url}, "extractor")
        self.assertEqual(result["status"], "captcha")
        self.assertEqual(page.visits, [url])

    def test_existing_capture_is_skipped_on_resume(self):
        url = "https://mahatenders.gov.in/nicgep/app?example=3"
        SCRATCH_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=SCRATCH_DIR) as temporary:
            manifest_path = Path(temporary) / "manifest.jsonl"
            output_path = Path(temporary) / "capture.jsonl"
            manifest_path.write_text(json.dumps({"sequence": 1, "url": url, "already_recorded": False}) + "\n", encoding="utf-8")
            output_path.write_text(json.dumps({"url": url, "status": "captured", "fields": {}}) + "\n", encoding="utf-8")
            remaining, count = capture_script.load_work(manifest_path, output_path, True)
        self.assertEqual(remaining, [])
        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
