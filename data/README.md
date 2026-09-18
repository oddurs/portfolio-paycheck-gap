# Source snapshots

`current.json` selects the reviewed snapshot used by the reproducible build.
Each directory under `snapshots/` is immutable and contains:

- the exact source response bytes under `raw/`;
- deterministic, UTF-8/LF normalized inputs under `normalized/`; and
- `manifest.json`, which records source URLs and identifiers, units, retrieval
  time, release periods, coverage, parser version, file sizes, and SHA-256
  checksums.

Manifest schema 2 records `raw_bundle_sha256` for every source. The bundle hash
is SHA-256 over each raw filename and its exact bytes in manifest order. Every
filename and byte payload is prefixed by its unsigned 64-bit big-endian byte
length, preventing ambiguous concatenation. Snapshot verification recalculates
both individual and bundle hashes.

Verify the selected snapshot without network access:

```sh
uv run python -c 'from pathlib import Path; from ppg_index.sources import resolve_current, verify_snapshot; p = resolve_current(Path("data")); assert p; verify_snapshot(p); print(p)'
```

Acquire a new candidate in the ignored working cache:

```sh
ppg fetch --cache-dir data/cache
```

An append-only source update is accepted automatically after validation. If a
value in an overlapping period changes or a prior period disappears, the
command stores the exact candidate under `quarantine/` and stops before
changing `current.json`. Inspect and explain the retained revision, then use
`--accept-revision` only after review. `--retrieved-at` exists for reproducible
fixtures and must not be used to misstate a live retrieval time.

`current.json` may also pin `artifact_generated_at`. This is the actual release
build time, kept separate from the source retrieval timestamp so a clean
checkout can reproduce provenance byte for byte.

The raw and derived data retain their source-specific terms. In particular,
the JKP market source and outputs derived from it are CC BY-NC 4.0 and limited
to noncommercial use. See [`DATA_LICENSE.md`](../DATA_LICENSE.md).
