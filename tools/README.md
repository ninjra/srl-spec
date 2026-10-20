# Run the sample verification

This is an offline authoring/test utility, not a production SRL library. It verifies finite fixtures and the specified resource/evidence rules. It does not prove every history, implement persistence/concurrency or provide an independent semantic review.

Use CPython 3.12 in a clean checkout or an extracted supplement source archive. Create an isolated environment and install the locked published wheels:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r tools/requirements.lock
```

Then run this command from the source root:

```sh
.venv/bin/python tools/verify_profiles.py
```

On Windows use `.venv\Scripts\python.exe` for the environment's interpreter. The checker resolves its source root from its own file; `--root PATH` can select another copy. It requires no Git history, network access, account credentials, private paths or private data after dependency installation. It exits nonzero on a failed predicate and prints a JSON report only after all checks pass. Python optimized execution is refused.

`--b3sum PATH` optionally compares BLAKE3 results with an independently installed official `b3sum`; if requested but unavailable it fails rather than silently skipping. OpenSSL SHA-256 comparison is used when OpenSSL is installed and is reported explicitly. The default checks use pinned BLAKE3 and CBOR packages, standard-library SHA-256, hand-derived integer literals and primary known hash anchors. They never count an unavailable optional tool as a completed comparison.

The report covers 91 source/codec/rejection/operation fixtures, resource boundary and aggregate refusal cases, fixed-domain condition projection/defaults, detecting mutations, local documentation links and the exact original six protected core-release files. Profile identifiers are enumerated explicitly; an unknown identifier cannot fall through to the test hash. Huge mathematical length branches are specified rather than empirically allocated at their native limits.

Dependencies are pinned by version and distribution SHA-256 in `requirements.lock`. Only published wheels are enabled; platforms without a listed CPython 3.12 wheel fail installation explicitly. Pinning fixes supplied artifact bytes; it is not a security certificate for their implementation. The CI workflow uses pinned action commits and read-only repository permissions, runs this same checker and does not publish anything.

Two complete successful runs on identical bytes demonstrate repeatable checks. **Independent semantic review was not performed for this supplement and was explicitly excluded by the owner.** The checker must never label these repeated runs as such a review or an implementation conformance proof.

The verification-tool license is specified in [LICENSE-TOOLS](../LICENSE-TOOLS). The specification and profile text retain their separately stated CC BY 4.0 license.
