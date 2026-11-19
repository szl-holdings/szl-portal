"""Command line: szlholdings <snapshot|alignment|coverage> [--json]."""
from __future__ import annotations

import argparse
import json
import sys

from .alignment import alignment_matrix, coverage, load_bundled_map
from .inventory import estate_snapshot, summarize


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="szlholdings", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_snap = sub.add_parser("snapshot", help="live GitHub + HF inventory")
    p_align = sub.add_parser("alignment", help="HF asset -> GitHub source matrix")
    p_cov = sub.add_parser("coverage", help="alignment coverage stats (bundled map)")
    for p in (p_snap, p_align, p_cov):
        p.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    if args.cmd == "snapshot":
        data = estate_snapshot()
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            s = data["summary"]
            print(f"GitHub {s['github']['org']}: {s['github']['repos_active']} active / "
                  f"{s['github']['repos_total']} repos")
            print(f"Hugging Face {s['huggingface']['org']}: "
                  f"{s['huggingface']['models_public']} public models, "
                  f"{s['huggingface']['datasets_public']} public datasets")
            print(f"snapshot: {s['generated_utc']}")
    elif args.cmd == "coverage":
        data = coverage(load_bundled_map())
        print(json.dumps(data, indent=2) if args.json else
              f"alignment coverage: {data['mapped']}/{data['total']} ({data['mapped_pct']}%) "
              f"[map generated {data['generated']}]")
    elif args.cmd == "alignment":
        amap = load_bundled_map()
        rows = alignment_matrix(amap)
        print(json.dumps(rows, indent=2) if args.json else
              "\n".join(f"{r['asset']} -> {r['source_repo'] or 'UNMAPPED'}"
                        f" [{r['method']}]" for r in rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
