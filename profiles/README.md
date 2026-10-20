# Concrete SRL sample profiles

Start with **[SRL-SHA256-1/1.0.0](SRL-SHA256-1.md)**. The alternative **[SRL-RAW-1/1.0.0](SRL-RAW-1.md)** preserves the supplied proposal's BLAKE3/CBOR approach. Both define actual encoding and operating choices; neither is an implementation or an implementation conformance certificate.

| Choice | Recommended sample | Alternative sample |
| --- | --- | --- |
| Full profile identifier | `SRL-SHA256-1/1.0.0` | `SRL-RAW-1/1.0.0` |
| Hash for all enabled values | SHA-256 | Unkeyed BLAKE3, first 32 output bytes |
| Address representation | Raw 32 bytes | Raw 32 bytes |
| Record encoding | `SRL-CBOR-1/1.0.0` | Same encoding |
| Complete operational rules | [COMMON-1/1.0.0](COMMON-1.md) | Same common rules |
| Supported scope | Sequential trusted reference state, specified access/delivery faults | Same scope |
| Interchange checks | [Exact vectors and scenarios](VECTORS.md) | Same vector format |

Use the hash-specific document **and** COMMON-1 together. COMMON-1 fixes all seven profile-declaration components in SRL §2.3: addressing/encoding, exact verification, complete evidence conditions, assessment and selection, aggregate resources, and operating scope. Its recovery and injectivity argument covers every mathematical body, including values refused by the sample's operational limits.

## What was absorbed and adjusted

The supplied proposal contributed the design intent. The documents here independently specify the contract; they do not import a library implementation or adopt the proposal as a monolithic standard.

| Supplied idea | Decision in these samples |
| --- | --- |
| 32-byte BLAKE3 addresses | Retained in SRL-RAW-1; SHA-256 supplied as the recommended alternative, without a performance claim |
| Fixed `[1, targets, statement]` CBOR shape | Retained with exact canonical field rules and a recovery argument |
| No tags and only ordinary unsigned integers | Amended: positive bignums above 64 bits preserve SRL's unbounded `Nat`; operational limits still refuse oversized offsets |
| Definite lengths everywhere | Retained for all enabled records; uniquely specified huge-length forms keep mathematical `E` total over all finite bodies |
| Hash all finite bytes using a bounded-input standard algorithm | Amended: explicit mathematical completion beyond the native bound; no security claim for that branch and no enabled writes there |
| Exact reads, comparisons and catalogue answers | Retained with a concrete evidence-slot/verifier model and stated trust/fault assumptions |
| Fixed error priority | Retained among established failures; supplemented by explicit validation, preflight and evidence phases |
| Example deployment limits | Made fixed sample policy, with state bounds, exact aggregate accounting and preflight order; other policies identify different complete profiles |
| Per-address serialization or transactions | Retained atomic outcome requirement; no claim that per-address locks alone establish a same-pre-state admission or durability |
| Recovery must not infer admission from stored encoding | Retained as a preservation obligation; crash recovery itself is outside these sequential samples' supported scope |
| Test vectors and synthetic collisions | Included separately: actual hash/encoding vectors, operational scenarios and an explicitly different test-only hash profile |

The total-function completions are explicit because SRL's mathematical domains are larger than the standard algorithms' native length fields. They introduce no new cryptographic design and no new enabled giant-input behavior. Exact equality and collision refusal continue to apply throughout the core contract.

## Status and versioning

These **sample profile specifications, version 1.0.0**, are additive repository material. They were added after the [SRL-SPEC v1.0.0 release](https://github.com/ninjra/srl-spec/releases/tag/v1.0.0) and are **not files in that release or its Zenodo deposit**. The published specification/PDF, manifest, release tag and deposit files retain their original bytes. The core specification version remains 1.0.0.

Future profile revisions must identify the exact common-rule version and hash rule they use. A change to evidence, assessment, resources or scope changes a complete profile even if `H` and `E` stay the same. There is no automatic migration, negotiation or claim of Web Annotation compatibility. A future normative core amendment must have its own version and release record.

The [clarification record](../CLARIFICATIONS.md) addresses evidence completeness, membership and the distinction between abstract semantics and a concrete realization. [VECTORS.md](VECTORS.md) states the fixture format, scope and verification limits.

Author: Shri Narayan Justin Ram; affiliation and publisher: Mushku Nobleworks. Copyright 2026 Mushku Nobleworks. Profile specification text: [CC BY 4.0](../LICENSE).
