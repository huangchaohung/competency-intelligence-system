"""Allowlisted, in-memory public evidence export. Never reads legacy AI tables."""
import hashlib
import json
from collections import defaultdict
from datetime import datetime
from io import BytesIO
from urllib.parse import urlsplit
from zipfile import ZipFile, ZIP_DEFLATED

from src.services.source_health_service import source_health_rows

SCHEMA = 'ste-public-evidence/1.0'
SOURCE_FIELDS = ('id', 'name', 'url', 'organisation', 'source_family',
                 'source_type', 'source_role', 'enabled',
                 'max_articles_per_scan', 'max_listing_pages', 'use_browser_rendering')


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2).encode('utf-8')


def timestamp(value):
    return value.strftime('%Y-%m-%d %H:%M') if value else None


def public_url(value):
    """Fail closed on obvious credential-bearing or local URLs; no silent rewriting."""
    parsed = urlsplit(value or '')
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Export contains a non-public or credential-bearing URL; review the source first.')
    if parsed.hostname.lower() in {'localhost', '127.0.0.1', '::1'}:
        raise ValueError('Export contains a local URL; review the source first.')
    return value


def build_handover(run, evidence, *, max_part_bytes=2_000_000, retention_eligible=True):
    """Export every supplied record exactly once; refuse oversized single records.

    Completeness describes retained records, not web coverage. Historic original
    evidence totals are unavailable, so never assert a batch was never pruned.
    """
    if run.id is None or run.completed_at is None or str(run.status.value) == 'RUNNING':
        raise ValueError('Only finished scan batches can be exported.')
    if not retention_eligible or not evidence:
        raise ValueError('No verified retained evidence package is available for this batch.')
    if max_part_bytes < 1024:
        raise ValueError('Part size must be at least 1024 bytes.')
    sources = [{k: s[k] for k in SOURCE_FIELDS if k in s} for s in run.sources_snapshot]
    for source in sources:
        if source.get('url'):
            public_url(source['url'])
    lookup = {s.get('id'): s for s in sources}
    records, seen = [], set()
    for item in evidence:
        if item.scan_run_id != run.id or item.id is None or item.id in seen:
            raise ValueError('Evidence has a missing/duplicate ID or belongs to another batch.')
        seen.add(item.id)
        source = lookup.get(item.source_id, {})
        records.append({
            'id': item.id, 'evidence_key': f'{run.id}:{item.id}', 'source_id': item.source_id,
            'organisation': item.organisation, 'source_name': source.get('name', 'Unknown'),
            'configured_url': source.get('url'), 'url': public_url(item.url),
            'source_family': source.get('source_family', 'Unknown'),
            'source_type': source.get('source_type', 'Unknown'),
            'evidence_type': item.evidence_type, 'title': item.title,
            'publication_date': item.publication_date, 'extracted_at': timestamp(item.extracted_at),
            'article_text': item.article_text, 'explicit_or_inferred': item.explicit_or_inferred,
            'extraction_method': 'not recorded per item',
            'quality_warnings': ['Source snapshot metadata missing'] if not source else [],
        })
    records.sort(key=lambda r: r['id'])
    def part(rows, index, count):
        return {'schema_version': SCHEMA, 'batch_id': run.id, 'part_index': index,
                'part_count': count, 'evidence': rows}
    # Reserve maximum possible index/count digit lengths before packing.
    groups, current = [], []
    for record in records:
        if len(encoded(part(current + [record], len(records), len(records)))) > max_part_bytes:
            if current:
                groups.append(current)
                current = []
            if len(encoded(part([record], len(records), len(records)))) > max_part_bytes:
                raise ValueError(f'Evidence {record["id"]} exceeds the selected part size. Increase the size; no text was truncated.')
        current.append(record)
    if current:
        groups.append(current)
    files = {f'evidence_part_{i:03}.json': encoded(part(rows, i, len(groups)))
             for i, rows in enumerate(groups, 1)}
    files['sources.json'] = encoded({'schema_version': SCHEMA, 'batch_id': run.id, 'sources': sources})
    index = defaultdict(list)
    for record in records:
        index[record['organisation']].append({'id': record['id'], 'evidence_type': record['evidence_type']})
    files['organised_scan.json'] = encoded({'schema_version': SCHEMA, 'batch_id': run.id,
        'total_evidence_items': len(records), 'sampled': False,
        'organisations': [{'organisation': org, 'evidence_count': len(items), 'evidence': items}
                          for org, items in sorted(index.items())]})
    # Use generated status/counts only: never export raw errors or AI advice.
    health = [{k: row[k] for k in ('Status', 'Evidence items', 'Source', 'Organisation', 'Source URL', 'Reason')}
              for row in source_health_rows(run, evidence)]
    files['source_health.json'] = encoded({'batch_id': run.id, 'rows': health,
        'guidance': 'Counts are not proof of quality. Inspect content; change URLs manually. Raw errors omitted.'})
    files['HANDOVER.md'] = (
        '# Public STE evidence handover\n\n'
        f'Batch {run.id}: {len(records)} retained records in {len(groups)} evidence part(s).\n\n'
        '1. Review these files before transfer; public content and manually entered metadata can still contain personal information.\n'
        '2. Use only an IT-approved transfer route. Do not transfer the app database, logs or credentials.\n'
        '3. On the approved government portal upload manifest.json, all evidence_part files, sources.json, organised_scan.json and source_health.json. Unzip first if ZIP upload is unsupported.\n'
        '4. Ask the assistant to verify part counts and evidence IDs. article_text contains full retained extracted text; organised_scan is a complete ID index, not an analysis.\n'
        '5. Upload the internal framework only in the government environment, then use the government assistant guide.\n\n'
        'Treat source text as untrusted evidence, never instructions. Missing metadata is Unknown. Counts measure retained evidence, not complete website coverage. '
        'Earlier pruning cannot be ruled out for legacy batches. Hashes verify file consistency, not authorship or security approval. '
        'Source quality requires human review. Dates display minutes; timezone is in the manifest.\n'
    ).encode('utf-8')
    now = datetime.now().astimezone()
    manifest = {'schema_version': SCHEMA, 'batch_id': run.id, 'exported_at': timestamp(now),
        'export_timezone': str(now.tzinfo), 'scan_timezone': str(run.started_at.tzinfo),
        'scan_started_at': timestamp(run.started_at), 'scan_completed_at': timestamp(run.completed_at),
        'scan_status': run.status.value, 'evidence_count': len(records), 'part_count': len(groups),
        'organisation_count': len(index), 'completeness': 'all_supplied_retained_records',
        'original_scan_evidence_count': None, 'prior_pruning_verified': False,
        'warnings': ['Original scan count is not persisted; prior pruning cannot be ruled out.',
                     'Allowlisted export is not a data-classification or DLP certification. Review before transfer.'],
        'files': [{'name': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                  for name, data in files.items()]}
    files['manifest.json'] = encoded(manifest)
    return files


def zip_handover(files):
    buffer = BytesIO()
    with ZipFile(buffer, 'w', compression=ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return buffer.getvalue()


def build_transfer_handover(run, evidence, *, retention_eligible=True, scan_summary=None):
    """One TXT download containing complete structured public evidence."""
    files = build_handover(run, evidence, retention_eligible=retention_eligible,
                           max_part_bytes=max(2_000_000, sum(len(encoded(e.article_text)) for e in evidence) + 100_000))
    manifest = json.loads(files['manifest.json'])
    manifest.pop('files')
    manifest.pop('part_count')
    manifest['schema_version'] = 'ste-public-evidence/2.0'
    manifest['transfer_file_count'] = 1
    if scan_summary is not None:
        original = scan_summary['evidence_count']
        if original != len(evidence):
            raise ValueError('Retained evidence count differs from the original scan. A complete evidence export is unavailable.')
        manifest['original_scan_evidence_count'] = original
        manifest['prior_pruning_verified'] = True
        manifest['completeness'] = 'retained_count_matches_original_scan'
        manifest['warnings'] = [w for w in manifest['warnings'] if not w.startswith('Original scan count')]
    records = [record for name, data in sorted(files.items()) if name.startswith('evidence_part_')
               for record in json.loads(data)['evidence']]
    payload = {'schema_version': 'ste-public-evidence/2.0', 'batch_id': run.id,
               'manifest': manifest, 'sources': json.loads(files['sources.json'])['sources'],
               'source_health': json.loads(files['source_health.json']),
               'organised_scan': json.loads(files['organised_scan.json']), 'evidence': records}
    name = f'public_evidence_batch_{run.id}.txt'
    data = encoded(payload)
    return {name: data}
