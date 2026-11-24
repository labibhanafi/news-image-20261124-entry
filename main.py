#!/usr/bin/env python3
"""news-image-20261124 entrypoint (Python 3.13, stdlib only).

Copies the entry image shipped in this repository to /output/entry.png
and verifies its bytes against the pinned SHA-256, so both grader runs
write identical output. No network, no randomness, no environment input.
"""
import hashlib
import os
import shutil
import sys
from pathlib import Path

ENTRY_SHA256 = "2970cff5ca75502c86e383b5f36ea832928939911b000ed62470fdd1419f3a2c"
ENTRY_NAME = "entry.png"


def main() -> int:
    here = Path(__file__).resolve().parent
    src = here / ENTRY_NAME
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / ENTRY_NAME
    shutil.copyfile(src, dst)
    data = dst.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        print("entry.png is not a PNG file", file=sys.stderr)
        return 1
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if (width, height) != (1024, 1024):
        print(f"entry.png is {width}x{height}, expected 1024x1024",
              file=sys.stderr)
        return 1
    if not 450_000 <= len(data) <= 600_000:
        print(f"entry.png is {len(data)} bytes, expected 450000-600000",
              file=sys.stderr)
        return 1
    digest = hashlib.sha256(data).hexdigest()
    if digest != ENTRY_SHA256:
        print(f"entry.png sha256 mismatch: got {digest}", file=sys.stderr)
        return 1
    print(f"wrote {dst} {len(data)} bytes sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
