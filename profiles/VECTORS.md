# SRL sample vectors, format version 1.0.0

[vectors.json](vectors.json) contains exact data for `SRL-SHA256-1/1.0.1` and `SRL-RAW-1/1.0.1`, defined by their hash documents and [COMMON-1/1.0.1](COMMON-1.md). It includes a separately identified synthetic hash profile for collision checks. These are finite fixtures and expected results, not a conforming library implementation or a proof of all SRL histories.

## Fixture format

All byte values use even-length lowercase hexadecimal for display; decode them before hashing, comparing or CBOR encoding. Offsets are decimal **strings** so JSON readers cannot round values above their exact integer range. Convert them to exact natural numbers. Byte lengths count decoded bytes. Objects in the fixture file are a transport for tests, not a new SRL request wire protocol.

| Field | Interpretation |
| --- | --- |
| `source_vectors` | Twelve empty/short-source hash anchors across the two algorithms |
| `codec_vectors` | Thirteen abstract bodies, exact canonical encoding bytes and identities under both hashes; includes integer-width boundaries, offsets above 64 bits, repeated/reordered targets and arbitrary statement bytes |
| `noncanonical_or_invalid_encodings` | Eight examples that are not canonical body encodings; reject as codec inputs, without adding a new public SRL failure |
| `operation_traces` | Two 27-step traces under the actual sample hashes and a four-step synthetic collision trace; each starts with its stated empty maps |

Each body has a nonempty `targets` list of `address_hex`, `start`, `end` and `commitment_hex` fields, plus `statement_hex`. Codec fixtures can encode bodies with invalid grounding or offsets exceeding operational limits. Correct encoding does not make them admissible.

Each operation step contains a request, complete conditions in compact notation, and the exact expected outcome and full post-state. `Success` has one of `address_hex`, `bytes_hex`, `body` or `sentinel: NotInCatalogue`; `Failure` has one of SRL's six errors. State `S` maps displayed addresses to byte strings; state `R` maps displayed identities to bodies. Compare full maps, including every old binding, after **every** step, especially failed admissions.

`conditions.default: permitted-exact` means: enumerate all relevant slots from COMMON-1 §2 against that step's pre-state and request; assign `permitted=true` and the exact expected `Bytes`, `Body` or `Absent` observation to each. Then apply the listed overrides to the exact slot key. Unspecified override fields retain their default. This is an explicit finite expansion rule, not permission to omit required evidence or substitute an unknown observation with an absent one. Preflight may terminate before reading those conditions.

## Expected behavior covered

The actual-hash traces cover all five operations: empty retention/read, exact middle-byte selection, empty statements, idempotent successful repetition, storage of an encoding without admission, later admission of that encoding, whole-encoding selection, repeated/reordered target positions and multiple sources. Refusals cover invalid request structure, missing/unknown/denied evidence, exact contrary delivery, bounds and slice-identifier failures, an oversized natural offset, and atomic rejection when a later target fails. Multi-failure cases distinguish established bounds from unknown evidence and select integrity failure over an independently invalid interval.

The constant-hash trace has the full test-only identifier **`SRL-TEST-CONSTANT-0/1.0.1`**. It replaces `H` with `H(b)=32 zero bytes` for every byte sequence; `Address`, `E` and the common reference rules remain unchanged. This is a different profile, with no cryptographic security claim. It retains `61`, rejects conflicting `62`, rejects an otherwise grounded admission whose encoding conflicts at that occupied address, and refuses a delivered `62` in place of retained `61` despite their equal hash. Both named real-hash samples retain their actual algorithms throughout. Synthetic collisions neither demonstrate practical collisions in those algorithms nor prove a production verifier detects every corruption.

## Reproducing checks

1. Check source hashes using the specified raw-byte hash modes. For BLAKE3 use default unkeyed hash output, first 32 bytes; SHA-256 uses standard raw digest bytes.
2. Independently encode each abstract body using COMMON-1's canonical grammar, compare every encoding byte and identity, decode and recover every field. Reject each invalid/noncanonical encoding, including trailing bytes and small integers encoded as bignums.
3. Expand each step's conditions and evaluate the fixed preflight, evidence and transition rules against the preceding state. Compare the full outcome and full post-state. Repeat from a fresh empty state for each trace.
4. Check policy boundaries with exact arithmetic. For example, with a retained 64 MiB source and six repeated one-byte valid targets, target reservations alone are `6 × (3 × 64 MiB + 3) = 1,207,959,570`, already greater than the 1 GiB whole-admission reservation. Each target alone fits. Adding the encoding/publication terms cannot make the complete admission fit. No target budget resets and no partial publication are permitted. Also check each maximum at equality and one above, treating oversized natural offsets as resource refusal rather than malformed structure.

Authoring verification compared independently assembled encodings with an external CBOR encoder/decoder, checked integer-boundary literals, compared actual hashes with official BLAKE3 test vectors and `b3sum` plus SHA-256 tooling, and evaluated all expected trace outcomes/post-states against a separately written rule evaluator. Changed fixture bytes, hashes and post-state mutations were required to fail verification. The [public offline checker](../tools/README.md) reproduces the fixtures, boundary checks and detecting mutations; its report identifies optional external hash-tool comparisons actually used. It also rejects unknown profile identifiers and checks finite evidence projection/defaults. The executable is a fixture-checking utility; no production SRL library is supplied.

Independent semantic review was not performed and was explicitly excluded by the owner. Two successful runs on identical bytes establish repeatable checks and must not be reported as independent reviews. The release verification report records the exact executed checks and actual CI run separately from this claim boundary.

The astronomically large byte-string/array branches of COMMON-1's total encoding and the beyond-native-domain hash completions are specified mathematically; they were not materialized as giant allocations or empirically tested at their native limits. Their totality/recovery arguments and excluded operational scope must not be confused with finite test execution. These checks establish the listed fixture predicates; realization, concurrency, recovery and security claims need their own evidence.

Author: Shri Narayan Justin Ram; affiliation and publisher: Mushku Nobleworks. Copyright 2026 Mushku Nobleworks. This specification text and its authored fixture tables: [CC BY 4.0](../LICENSE).
