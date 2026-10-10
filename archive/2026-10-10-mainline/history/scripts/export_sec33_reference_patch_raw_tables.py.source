"""Export supplied whole-label FRAGSTATS tables without changing their values.

No model, landscape metric, or spatial analysis is run. CSV uses UTF-8 with BOM
for direct spreadsheet opening. All numeric literals retain the source precision.
"""
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'legacy/experiment-results/label'
OUTPUT = ROOT / 'results/raw/sec33_reference_patch_types'
FIELDS = ['LID', 'PID', 'TYPE', 'AREA', 'GYRATE', 'SHAPE', 'CONTIG', 'ENN']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return [[cell.strip() for cell in row] for row in csv.reader(handle)
                if any(cell.strip() for cell in row)]


def adjacency_rows(source):
    original = rows(source)
    result = [['LID', 'CLASS_FROM', 'CLASS_TO', 'ADJACENCIES']]
    lid = None
    targets = None
    for row in original:
        if len(row) == 1:
            lid = row[0]
            targets = None
        elif row[0] == 'Class ID / ID':
            assert lid is not None, source
            targets = row[1:]
        else:
            assert lid and targets and row[0] == '', (source, row)
            assert len(row) == len(targets) + 2, (source, row)
            for target, value in zip(targets, row[2:]):
                assert int(value) >= 0, (source, value)
                result.append([lid, row[1], target, value])
    # Reconstruct each original block and verify every original matrix cell.
    blocks = []
    cursor = 1
    for row in original:
        if len(row) == 1:
            blocks.append(row)
            lid = row[0]
        elif row[0] == 'Class ID / ID':
            blocks.append(row)
            targets = row[1:]
        else:
            group = result[cursor:cursor + len(targets)]
            assert all(r[:2] == [lid, row[1]] for r in group)
            assert [r[2] for r in group] == targets
            blocks.append(['', row[1]] + [r[3] for r in group])
            cursor += len(targets)
    assert blocks == original and cursor == len(result), source
    return result


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    previous = json.loads((ROOT / 'results/summary/sec33_reference_patch_types/prepare_manifest.json').read_text(encoding='utf-8'))
    known = {Path(item['path']).resolve(): item['sha256'] for item in previous['inputs']}
    inventory = []
    sources = sorted(SOURCE.glob('*.patch')) + sorted(SOURCE.glob('*.adj'))
    sources += sorted((SOURCE / 'fragstats_results').glob('完整标签*.csv'))
    assert len(sources) == 11, [p.name for p in sources]
    for source in sources:
        digest = sha(source)
        if source.resolve() in known:
            assert digest == known[source.resolve()], ('source changed since analysis', source)
        if source.suffix == '.patch':
            table = rows(source)
            assert table[0] == FIELDS, source
            name = source.stem + '_patch.csv'
            conversion = 'Whitespace trimmed; original columns, row order, duplicates and numeric literals preserved.'
        elif source.suffix == '.adj':
            table = adjacency_rows(source)
            name = source.stem + '_adjacency.csv'
            conversion = 'Original matrix blocks reshaped to LID/from/to/count; every matrix cell retained and reconstructed.'
        else:
            table = rows(source)
            name = source.name
            conversion = 'Existing full-label background CSV; field text and row order preserved.'
        assert all(len(row) == len(table[0]) for row in table), source
        buffer = io.StringIO(newline='')
        writer = csv.writer(buffer, lineterminator='\n')
        writer.writerows(table)
        data = buffer.getvalue().encode('utf-8-sig')
        destination = OUTPUT / name
        if destination.exists():
            assert destination.read_bytes() == data, ('refusing to overwrite changed export', destination)
        else:
            destination.write_bytes(data)
        assert rows(destination) == table, ('CSV round trip changed fields', destination)
        assert sha(source) == digest, ('source changed during export', source)
        by_lid = dict(Counter(row[0] for row in table[1:])) if table[0][0] == 'LID' else None
        inventory.append(dict(source=str(source.relative_to(ROOT)).replace('\\', '/'),
                              source_sha256=digest, source_bytes=source.stat().st_size,
                              output=str(destination.relative_to(ROOT)).replace('\\', '/'),
                              output_sha256=sha(destination), output_bytes=len(data),
                              rows=len(table)-1, columns=table[0], rows_by_lid=by_lid,
                              conversion=conversion, status='Verified'))
        print(name, len(table)-1, 'rows: Verified')
    manifest = dict(created_at_utc=datetime.now(timezone.utc).isoformat(),
                    data_status='real; format conversion of supplied experimental outputs',
                    status='Verified', numeric_recalculation=False,
                    verification='All exported cells compared as strings after trimming layout whitespace; adjacency blocks reconstructed exactly; originals unchanged.',
                    script='scripts/export_sec33_reference_patch_raw_tables.py',
                    script_sha256=sha(Path(__file__)), tables=inventory)
    path = OUTPUT / 'conversion_manifest.json'
    if path.exists():
        existing = json.loads(path.read_text(encoding='utf-8'))
        assert existing['tables'] == inventory and existing['script_sha256'] == manifest['script_sha256'], 'manifest differs; preserve existing export'
    else:
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
