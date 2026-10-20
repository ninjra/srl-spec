# Sample profile changes

## 1.0.1 — independently versioned supplement

- Replace request-dependent condition-domain notation with one fixed total function domain and an explicit finite projection. Missing concrete evidence defaults to Unknown; it never becomes absence or success.
- Add a portable offline checker, hash-pinned CPython 3.12 dependencies, documented invocation and CI with pinned actions/read-only permissions. Unknown profile identifiers are rejected explicitly.
- Add immutable supplement packaging, manifest, signed tag/assets and a separate linked Zenodo deposit. Preserve all original SRL-SPEC 1.0.0 release artifacts.
- State the assurance boundary explicitly: independent semantic review was excluded by the owner and is not counted as completed review. Repeated checks, software verification and publication custody remain distinct.
- License the new verification software and associated utility/CI material under MIT by owner approval; keep specification/profile text and authored fixtures under CC BY 4.0.

The actual enabled hash rules, canonical encoding `SRL-CBOR-1/1.0.0`, resource formulas/limits `SRL-SAMPLE-LIMITS-1/1.0.0`, six errors and five core operations are unchanged. Fixture metadata uses the corrected complete-profile identifiers; fixture byte payloads and expected outcomes are preserved.

## 1.0.0 — initial repository samples

Initial BLAKE3 and recommended SHA-256 samples, common encoding/evidence/resource rules, exact fixture data and clarification record were added at repository commit `59b9661eefec974f520309bc2acc1019f2190b15`. They were later repository additions and were not part of the original core `v1.0.0` release or its Zenodo files. They remain preserved in Git history.
