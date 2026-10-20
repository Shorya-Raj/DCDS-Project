"""Meaningful checks for the query explorer's filter and read-only boundaries."""
from datetime import date
import unittest

from tender_explorer.query_tools import (
    filtered_tender_query, parse_mongo_filter, validate_sql_query,
)


class QueryToolsTests(unittest.TestCase):
    def test_filter_values_are_bound_separately(self):
        query, params = filtered_tender_query(
            ("Civil Works",), ("Civil Works", "Construction Works"),
            ("NASHIK",), "Road_%'", True, date(2026, 10, 19),
        )
        self.assertEqual(query.count("%s"), len(params))
        self.assertEqual(params, ("Civil Works", "NASHIK", "road_%'", "road_%'", "road_%'", date(2026, 10, 19)))
        self.assertNotIn("road_%'", query)
        self.assertIn("LOCATE(%s, LOWER(t.title))", query)
        self.assertIn("t.closing_date >= %s", query)

    def test_clearing_categories_returns_no_dashboard_rows(self):
        query, params = filtered_tender_query(
            (), ("Civil Works",), (), "", False, date(2026, 10, 19),
        )
        self.assertIn("WHERE 1 = 0", query)
        self.assertEqual(params, ())

    def test_sql_search_allows_select_and_quoted_search_text(self):
        query = "SELECT title FROM tenders WHERE title = 'delete; -- literal'"
        self.assertEqual(validate_sql_query(query), query)

    def test_sql_search_rejects_writes_and_multiple_statements(self):
        for query in (
            "DELETE FROM tenders",
            "SELECT * FROM tenders; DELETE FROM tenders",
            "SELECT * INTO OUTFILE 'x' FROM tenders",
            "SELECT SLEEP(5) FROM tenders",
            "SELECT * FROM tenders FOR UPDATE",
            "SELECT * FROM tenders FOR SHARE",
            "SELECT * FROM tenders -- comment",
        ):
            with self.subTest(query=query), self.assertRaises(ValueError):
                validate_sql_query(query)

    def test_mongo_filter_allows_simple_searches(self):
        parsed = parse_mongo_filter(
            '{"$and": [{"category": "Civil Works"}, {"closing_date": {"$gte": "2026-10-01"}}]}'
        )
        self.assertEqual(parsed["$and"][1]["closing_date"]["$gte"], "2026-10-01")

    def test_mongo_filter_rejects_commands_and_raw_fields(self):
        for filter_text in (
            '{"$where": "sleep(5000)"}',
            '{"raw_source_row": {"$exists": true}}',
            '{"category": {"$regex": "Civil"}}',
            '{"category": {"$in": []}}',
            '{"category": NaN}',
            '{"estimated_value_inr": 1e400}',
            '{"category": "Civil Works", "category": "Other"}',
            '["Civil Works"]',
        ):
            with self.subTest(filter_text=filter_text), self.assertRaises(ValueError):
                parse_mongo_filter(filter_text)


if __name__ == "__main__":
    unittest.main()
