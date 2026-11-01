#!/usr/bin/env python3
"""Validate the editorial forecast catalog without making network or paid API calls."""
import datetime as dt
import json
from pathlib import Path
from urllib.parse import urlparse


def validate(catalog, rhyme_ids):
    problems = []
    try:
        as_of = dt.date.fromisoformat(catalog['asOf'])
        review = dt.date.fromisoformat(catalog['reviewAfter'])
        if review <= as_of:
            problems.append('reviewAfter must follow asOf')
    except (KeyError, ValueError, TypeError):
        problems.append('valid asOf and reviewAfter dates are required')
        as_of = None
    sources = catalog.get('sources', {})
    for key, source in sources.items():
        url = urlparse(source.get('url', ''))
        if url.scheme != 'https' or not url.hostname or url.username or url.password:
            problems.append(f'{key}: source must be a public HTTPS URL')
        if not source.get('name') or not source.get('published'):
            problems.append(f'{key}: source name and publication date required')
        try:
            published = source['published']
            date = dt.date.fromisoformat(published + '-01' if len(published) == 7 else published)
            if as_of and date > as_of:
                problems.append(f'{key}: source cannot postdate the editorial review')
        except (KeyError, TypeError, ValueError):
            problems.append(f'{key}: invalid publication date')
    seen = set()
    for item in catalog.get('scenarios', []):
        key = item.get('id', '?')
        if key in seen:
            problems.append(f'{key}: duplicate scenario')
        seen.add(key)
        for field in ('id', 'title', 'projection', 'reading', 'stronger', 'weaker', 'limit'):
            if not isinstance(item.get(field), str) or not item[field].strip():
                problems.append(f'{key}: {field} is required')
        if item.get('source') not in sources:
            problems.append(f'{key}: unknown source')
        if item.get('rhyme') not in rhyme_ids:
            problems.append(f'{key}: unknown historical rhyme')
        if item.get('topic') not in {'money', 'tech', 'disaster', 'health', 'power', 'society'}:
            problems.append(f'{key}: invalid topic')
        start, end = item.get('from'), item.get('to')
        if type(start) is not int or type(end) is not int or not 2026 <= start <= end <= 2100:
            problems.append(f'{key}: invalid forecast window')
        if not isinstance(item.get('watch'), list) or not item['watch'] or any(not isinstance(x, str) or not x.strip() for x in item['watch']):
            problems.append(f'{key}: observable signals are required')
    if not seen:
        problems.append('at least one scenario is required')
    return problems


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    ids = {p['id'] for f in (root / 'data').glob('pairs-*.json') for p in json.loads(f.read_text())}
    errors = validate(json.loads((root / 'data/forecasts.json').read_text()), ids)
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Forecast catalog: sources, dates, evidence, windows and history links validated')
