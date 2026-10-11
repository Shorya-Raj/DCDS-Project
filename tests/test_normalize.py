import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from tender_explorer.normalize import (
    document_for,
    load_records,
    normalize_mahatenders_row,
    normalize_record,
    parse_money,
)
from tender_explorer.load_data import select_spread_sample

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample_tenders.json"


class NormalizeTests(unittest.TestCase):
    def test_money_units(self):
        self.assertEqual(parse_money("3.57 Cr."), Decimal("35700000.00"))
        self.assertEqual(parse_money("8.41 Lakh"), Decimal("841000.00"))
        self.assertEqual(parse_money("85.00 K"), Decimal("85000.00"))
        self.assertIsNone(parse_money("Refer Docs"))
        self.assertIsNone(parse_money(None))
        with self.assertRaises(ValueError):
            parse_money("unknown")

    def test_snapshot_validates_and_has_stable_ids(self):
        records = load_records(SAMPLE)
        self.assertEqual(len(records), 129)
        self.assertEqual(len({record["tender_key"] for record in records}), 129)
        self.assertTrue(all(record["tender_key"].startswith("tender247:") for record in records))

    def test_missing_details_are_not_invented(self):
        record = load_records(SAMPLE)[0]
        detail = document_for(record)
        self.assertIsNone(detail["eligibility"])
        self.assertIsNone(detail["corrigenda"])
        self.assertEqual(detail["_id"], record["tender_key"])

    def test_rejects_unexpected_source(self):
        record = load_records(SAMPLE)[0]["raw"].copy()
        record["sourceUrl"] = "https://example.com"
        with self.assertRaises(ValueError):
            normalize_record(record)

    def test_mahatenders_mapping_uses_tender_id_and_preserves_missing_values(self):
        raw = {
            "Tender ID": "2026_TEST_123_1",
            "Tender Reference No.": "PWD/1/2026",
            "Tender Title": "Drainage repair",
            "Organisation": "Test Municipal Corporation",
            "Tender Category": "Works",
            "Product Category": "Civil Works",
            "District / Location": "Nashik",
            "e-Published Date": "2026-10-03",
            "Closing Date": "2026-10-13",
            "Opening Date": datetime(2026, 10, 14),
            "Collected On": datetime(2026, 10, 3),
            "Estimated Value (INR)": 0,
            "EMD (INR)": None,
            "Eligibility / Conditions": None,
            "Source Detail URL": "https://mahatenders.gov.in/nicgep/app?page=FrontEndAdvancedSearchResult&sp=S1",
        }
        record = normalize_mahatenders_row(raw)
        detail = document_for(record)
        self.assertEqual(record["tender_key"], "2026_TEST_123_1")
        self.assertEqual(record["listing_id"], "2026_TEST_123_1")
        self.assertEqual(record["category"], "Civil Works")
        self.assertEqual(record["estimated_value_inr"], Decimal("0.00"))
        self.assertIsNone(record["emd_inr"])
        self.assertEqual(record["published_date"].isoformat(), "2026-10-03")
        self.assertEqual(detail["_id"], "2026_TEST_123_1")
        self.assertEqual(detail["categories"], ["Civil Works"])
        self.assertEqual(detail["estimated_value_inr"], 0)
        self.assertIsNone(detail["emd_inr"])
        self.assertEqual(detail["opening_date"], "2026-10-14")
        self.assertEqual(detail["status_collected_on"], "2026-10-03")
        self.assertIsNone(detail["eligibility"])
        self.assertIsNone(detail["document_names_or_links"])

    def test_spread_sample_is_deterministic_and_covers_full_input(self):
        records = [{"id": index} for index in range(100)]
        sample = select_spread_sample(records, 25)
        self.assertEqual(len(sample), 25)
        self.assertEqual(sample[0]["id"], 0)
        self.assertEqual(sample[-1]["id"], 99)
        self.assertEqual(sample, select_spread_sample(records, 25))
        self.assertEqual(len({record["id"] for record in sample}), 25)
        self.assertEqual(select_spread_sample(records, 1), [records[50]])

    def test_mahatenders_mapping_rejects_non_official_detail_url(self):
        raw = {
            "Tender ID": "2026_TEST_123_1",
            "Tender Title": "Drainage repair",
            "Organisation": "Test Municipal Corporation",
            "Tender Category": "Works",
            "Product Category": "Civil Works",
            "District / Location": "Nashik",
            "e-Published Date": "2026-10-03",
            "Closing Date": "2026-10-13",
            "Source Detail URL": "https://example.com/tender",
        }
        with self.assertRaises(ValueError):
            normalize_mahatenders_row(raw)


if __name__ == "__main__":
    unittest.main()

