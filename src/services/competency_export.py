"""Offline competency-card TXT export from the current session, never a new scan."""
import csv
import io
import json
from collections import Counter
from urllib.parse import urlsplit

from src.services.compact_evidence import build_compact_handover
from src.scanner.competency_pilot import qualification, make_card, serial, split_cards


def csv_bytes(rows, fields):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        writer.writerow({k: ("'" + v if isinstance(v, str) and v.startswith(('=', '+', '-', '@')) else v)
                         for k, v in row.items()})
    return stream.getvalue().encode('utf-8-sig')


def build_competency_handover(run, evidence, *, retention_eligible=True, scan_summary=None):
    native = (scan_summary or {}).get('competency_result')
    if native is not None:
        if native['run_id'] != run.id or not run.completed_at:
            raise ValueError('Card result does not belong to the completed scan')
        counts = Counter(c['parent_organisation'] for c in native['cards'])
        status_counts = {s['Parent_organisation']: int(s['cards_produced']) for s in native['statuses']}
        if any(status_counts.get(parent) != count for parent, count in counts.items()) or sum(status_counts.values()) != len(native['cards']):
            raise ValueError('Cards and organisation status disagree; export stopped')
        if sum(int(log.get('cards_produced', 0)) for log in native['logs']) != len(native['cards']):
            raise ValueError('Cards and URL log disagree; export stopped')
        logged = Counter()
        for log in native['logs']:
            if int(log.get('cards_produced', 0)):
                logged[(log.get('parent_organisation'), log.get('Scan_ID'), log.get('url'))] += int(log['cards_produced'])
        expected = Counter((c.get('parent_organisation'), c.get('scan_id'), c.get('url')) for c in native['cards'])
        if logged != expected:
            raise ValueError('Card provenance and URL log disagree; export stopped')
        identifier = native.get('export_id')
        if identifier:
            if any(c.get('export_id') != identifier for c in native['cards']):
                raise ValueError('Mixed scan identifiers; export stopped')
            native = dict(native, statuses=[dict(s, export_id=identifier) for s in native['statuses']],
                          logs=[dict(log, export_id=identifier) for log in native['logs']])
        files = {f'cards_part_{i:03}.txt': part.encode('utf-8') for i, part in enumerate(split_cards(native['cards']), 1)}
        files['organisation_status.txt'] = csv_bytes(native['statuses'], list(native['statuses'][0]) if native['statuses'] else ['Parent_organisation', 'Status'])
        files['url_log.txt'] = csv_bytes(native['logs'], list(native['logs'][0]) if native['logs'] else ['Scan_ID', 'url'])
        if identifier:
            files = {name.replace('.txt', f'_{identifier[:12]}.txt'): data for name, data in files.items()}
        return files
    # Reuse the existing public-URL, current-run and retained-count validation.
    validated = build_compact_handover(run, evidence, retention_eligible=retention_eligible, scan_summary=scan_summary)
    records = [r for data in validated.values() for r in json.loads(data)['evidence']]
    originals = {e.id: e for e in evidence}
    sources = {s.get('id'): s for s in run.sources_snapshot}
    used, source_counts = Counter(), Counter()
    cards, logs, seen = [], [], set()
    parents = dict.fromkeys(s.get('organisation', 'Unknown') for s in run.sources_snapshot)
    for record in records:
        parent = record['organisation']
        parents[parent] = None
        source = sources.get(record['source_id'], {})
        text = originals[record['id']].article_text
        blocks = [b.strip() for b in text.splitlines() if b.strip()]
        good, reason = qualification(record['url'], record['title'], record['title'], blocks)
        identity = (parent, record['url'])
        if identity in seen:
            good, reason = False, 'Duplicate organisation URL'
        row = dict(Scan_ID=f"S{record['source_id']}", Parent_organisation=parent,
                   Organisation_as_listed=parent, Mode='SCAN', Source_type=record['source_type'],
                   Max_chars_per_card=1000, _card_number=record['id'])
        if used[parent] >= 5000 or source_counts[record['source_id']] >= 4:
            good, reason = False, 'Export budget reached: 4 cards/source, 5000 characters/organisation'
        card = make_card(row, record['url'], record['title'], blocks, 5000-used[parent]) if good else None
        if good and not card:
            reason = 'No substantive excerpt fits character budget'
        if card:
            # Add metadata before enforcing the complete serialized-card limit.
            card.update(source_family=record['source_family'], publisher_host=urlsplit(record['url']).hostname,
                        retrieval_method='CRAWLER', evidence_id=record['id'],
                        excerpt_warning='Partial excerpt; do not infer omitted content or reconstruct PDF table relationships.')
            limit = min(1000, 5000-used[parent])
            while len(serial(card)) > limit and card['article_text']:
                card['article_text'] = card['article_text'].rsplit(' ', 1)[0] if ' ' in card['article_text'] else ''
            if len(card['article_text']) < 80:
                card, reason = None, 'Metadata leaves insufficient excerpt space'
        if card:
            cards.append(card)
            used[parent] += len(serial(card))
            source_counts[record['source_id']] += 1
            seen.add(identity)
        logs.append(dict(Scan_ID=row['Scan_ID'], parent_organisation=parent, configured_url=source.get('url',''),
                         url=record['url'], http_status='', rendering_used='Not recorded in stored evidence',
                         cards_produced=int(card is not None), chars=len(serial(card)) if card else 0,
                         reason_if_rejected=reason if not card else '', record_kind='RETAINED_EVIDENCE_EXPORT'))
    statuses = []
    for parent in parents:
        count = sum(c['parent_organisation'] == parent for c in cards)
        statuses.append(dict(Parent_organisation=parent, Status='SCANNED' if count else 'CRAWLER_UNAVAILABLE',
            cards_produced=count, chars_produced=used[parent],
            retained_evidence=sum(r['organisation'] == parent for r in records),
            reason='' if count else 'No qualifying cards in this export; review scan errors and export rejection reasons.',
            limitations='Selective deterministic excerpts, not full inventories. URL log covers retained records only; HTTP attempts were not persisted. Missing content never proves obsolescence.'))
    files = {f'cards_part_{i:03}.txt': part.encode('utf-8') for i, part in enumerate(split_cards(cards), 1)}
    files['organisation_status.txt'] = csv_bytes(statuses, list(statuses[0]))
    fields = ['Scan_ID','parent_organisation','configured_url','url','http_status','rendering_used','cards_produced','chars','reason_if_rejected','record_kind']
    files['url_log.txt'] = csv_bytes(logs, fields)
    return files
