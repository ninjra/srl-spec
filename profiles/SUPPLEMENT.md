# SRL Sample Profiles and Verification Supplement

**Supplement version 1.0.1.** Author: Shri Narayan Justin Ram ([ORCID 0009-0008-3593-2816](https://orcid.org/0009-0008-3593-2816)); affiliation and publisher: Mushku Nobleworks.

Supplement DOI: [10.5281/zenodo.23513927](https://doi.org/10.5281/zenodo.23513927). This identifier is reserved during preparation and becomes a publication link only when the supplement is published. The release assets and Zenodo record identify actual publication status and date. Original core specification DOI: [10.5281/zenodo.23511373](https://doi.org/10.5281/zenodo.23511373).

This supplement supplies concrete profile choices and reproducible finite checks for SRL-SPEC 1.0.0. It adds no normative requirements to the core specification and does not replace its original published files.

| Material | Read or run |
| --- | --- |
| Recommended SHA-256 profile | [SRL-SHA256-1/1.0.1](SRL-SHA256-1.md) |
| BLAKE3 alternative | [SRL-RAW-1/1.0.1](SRL-RAW-1.md) |
| Exact encoding, conditions, assessment and resources | [COMMON-1/1.0.1](COMMON-1.md) |
| Fixed fixture bytes, results and scope | [VECTORS.md](VECTORS.md) and [vectors.json](vectors.json) |
| Portable offline checker | [tools/README.md](../tools/README.md) |
| Changes from the first repository profiles | [CHANGELOG.md](CHANGELOG.md) |

Version 1.0.1 fixes one condition domain independent of requests and states, with a finite request projection and explicit Unknown defaults for missing concrete evidence. The encoding identifier `SRL-CBOR-1/1.0.0` and numerical resource-policy identifier `SRL-SAMPLE-LIMITS-1/1.0.0` remain unchanged. A different complete profile must still identify its own evidence, resource and operating assumptions even when hash/encoding bytes agree.

The utility runs from a clean checkout or extracted archive with pinned dependencies. It checks exact source hashes/encodings, expected operations and whole post-states, refusal/atomicity cases, integer and resource boundaries, evidence projection, mutation rejection and protected original release artifacts. CI runs the same command. The supplement release's `VERIFICATION.json` records actual check/CI identities and exact artifact hashes; claims are bound to those records, not a generic badge.

**Assurance scope:** independent semantic review was not performed and was explicitly excluded by the owner. Repeated successful checker runs establish repeatability of the checks; they do not count as independent review. No production SRL library, proof of every history, concurrency/recovery implementation, cryptographic security certificate or patent/legal clearance is supplied.

The profile scope is sequential and assumes a correct protected reference state, control metadata and exact comparator. These are declared reference assumptions; future implementations must justify their concrete realization. Hash equality never replaces exact comparison, and decoding retained bytes never establishes catalogue admission.

The signed `profiles-v1.0.1` tag identifies the immutable supplement source. The release archive, manifest, verification report, detached SSH signatures and public key provide artifact verification material. The manifest excludes itself; archive/report signatures bind the complete packaged bytes. The original `v1.0.0` tag and original Zenodo deposit remain unchanged.

Copyright 2026 Mushku Nobleworks. Specification/profile text and authored fixtures: [CC BY 4.0](../LICENSE). Verification software, requirements, CI and utility usage documentation: [MIT](../LICENSE-TOOLS). These scopes allocate licenses by file; they are not a blanket dual license for every file. Third-party packages retain their own licenses.

The ideas and system design originate with Shri Narayan Justin Ram. AI tools assisted development and preparation; this supplement was prepared with assistance from OpenAI tools. No third-party SRL implementation is incorporated.
