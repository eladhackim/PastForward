import copy
import json
import unittest
from pathlib import Path
from check_forecasts import validate

ROOT = Path(__file__).resolve().parents[1]


class ForecastCatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((ROOT / 'data/forecasts.json').read_text())
        self.ids = {p['id'] for f in (ROOT / 'data').glob('pairs-*.json') for p in json.loads(f.read_text())}

    def test_published_catalog_has_traceable_evidence(self):
        self.assertEqual(validate(self.catalog, self.ids), [])

    def test_rejects_missing_source_and_unknown_history(self):
        row = self.catalog['scenarios'][0]
        row['source'], row['rhyme'] = 'unknown', 'unknown'
        errors = validate(self.catalog, self.ids)
        self.assertTrue(any('unknown source' in e for e in errors))
        self.assertTrue(any('unknown historical rhyme' in e for e in errors))

    def test_rejects_unsafe_or_embedded_credential_source_urls(self):
        for url in ['javascript:alert(1)', 'http://example.com', 'https://user:password@example.com']:
            with self.subTest(url=url):
                catalog = copy.deepcopy(self.catalog)
                catalog['sources']['imf-oct26']['url'] = url
                self.assertTrue(validate(catalog, self.ids))

    def test_rejects_inverted_and_non_numeric_windows(self):
        for start, end in [(2030, 2026), ('2026', 2027), (True, 2030)]:
            with self.subTest(window=(start, end)):
                row = self.catalog['scenarios'][0]
                row['from'], row['to'] = start, end
                self.assertTrue(any('forecast window' in e for e in validate(self.catalog, self.ids)))

    def test_requires_limits_and_observable_signals(self):
        row = self.catalog['scenarios'][0]
        row['watch'], row['limit'] = [], ''
        errors = validate(self.catalog, self.ids)
        self.assertTrue(any('observable signals' in e for e in errors))
        self.assertTrue(any('limit is required' in e for e in errors))

    def test_source_cannot_be_published_after_review(self):
        self.catalog['sources']['imf-oct26']['published'] = '2027-01-01'
        self.assertTrue(any('postdate' in e for e in validate(self.catalog, self.ids)))

    def test_requires_valid_editorial_review_dates(self):
        self.catalog['reviewAfter'] = self.catalog['asOf']
        self.assertTrue(any('reviewAfter' in e for e in validate(self.catalog, self.ids)))

    def test_duplicate_ids_and_empty_catalog_are_rejected(self):
        self.catalog['scenarios'].append(copy.deepcopy(self.catalog['scenarios'][0]))
        self.assertTrue(any('duplicate' in e for e in validate(self.catalog, self.ids)))
        self.catalog['scenarios'] = []
        self.assertTrue(any('at least one' in e for e in validate(self.catalog, self.ids)))


if __name__ == '__main__':
    unittest.main()
