"""Convert an existing public JSON-in-TXT export; no scan or AI request."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.services.compact_evidence import compact_payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    files = compact_payload(json.loads(args.input.read_text(encoding='utf-8-sig')))
    args.output.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        target = args.output / name
        with target.open('xb') as handle:
            handle.write(data)
        print(f'{target}: {len(data.decode("utf-8")):,} characters')


if __name__ == '__main__':
    main()
