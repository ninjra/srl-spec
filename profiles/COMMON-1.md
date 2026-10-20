# SRL sample profile common rules, version 1.0.0

These rules, together with exactly one named hash profile, define a complete sequential sample profile for [SRL-SPEC 1.0.0](../SPECIFICATION.md). They are requirements of those samples, not additional requirements on SRL generally. They specify behavior and encoding; no conforming implementation is supplied.

## 1. Domains and canonical record encoding

`Address` is every 32-byte sequence. Equality compares all bytes, including length where length is not fixed by the type. Hexadecimal in the examples is a display convention, never the hashed representation. `Nat`, `Bytes`, `Span` and `Body` retain their exact SRL domains, including arbitrary finite sizes and unbounded natural offsets.

The shared encoding identifier is **SRL-CBOR-1/1.0.0**. A body `(T,s)` encodes this CBOR value, with no surrounding envelope:

```text
[1, [[a, i, j, h], ...], s]
```

The outer array has three elements. Its first element is integer 1. The middle element is a nonempty array of four-element target arrays. `a` and `h` are byte strings of exactly 32 bytes; `i` and `j` are exact nonnegative integers; `s` is a byte string, including empty. Target order and repetitions are significant. No text strings, maps, floating point, negative integers, nulls, optional fields or byte normalization occur.

The following rules fix every encoding byte. Let `M = 2^64−1`. `head(m,n)` is the CBOR header of major type `m` with argument `0 ≤ n ≤ M`: inline for `n < 24`, otherwise additional information 24, 25, 26 or 27 followed by the smallest sufficient 1, 2, 4 or 8-byte unsigned big-endian argument. Multi-byte arguments have exactly that width.

| Value | Unique encoding |
| --- | --- |
| Natural `n ≤ M` | `head(0,n)` |
| Natural `n > M` | `c2` followed by the encoding of the shortest unsigned big-endian magnitude byte string of `n`, with no leading zero |
| Byte string `x`, `length(x) ≤ M` | `head(2,length(x))` followed by `x` |
| Byte string `x`, `length(x) > M` | `5f`, then consecutive definite byte-string chunks of exactly `M` bytes except the final chunk of 1 through `M` bytes, then `ff`; no empty chunk |
| Array `v`, `length(v) ≤ M` | `head(4,length(v))`, followed by each encoded element in order |
| Array `v`, `length(v) > M` | `9f`, followed by each encoded element in order, then `ff` |

Tag 2 (`c2`) is permitted only for offsets above `M`. Its magnitude uses the byte-string rule above. Indefinite forms are permitted only at the specified mathematical length thresholds; ordinary enabled records use definite arrays and byte strings. These exceptional forms make `E` total over all SRL bodies. They do not enable enormous operations. In the ordinary definite-length subset this follows RFC 8949's core deterministic encoding requirements; the huge-length extension is this profile's own unique rule, not a claim that RFC core deterministic encoding permits indefinite items.

**Recovery argument.** CBOR headers and definite payload lengths, or the specified break markers, uniquely delimit every item. The fixed array shape identifies every field. The two integer branches have disjoint value ranges and recover an exact natural. Byte strings recover their full byte sequences, including chunk concatenation in the huge-length branch. Array traversal recovers every target position and repetition. Thus parsing `E(r)` recovers exactly `r`; if `E(r)=E(r')`, this same recovery gives `r=r'`. Every finite body has a finite encoding. This establishes the encoding and recovery laws independently of operational size limits. Every encoding here is nonempty; SRL's permission for an empty encoding is optional.

A codec accepting this profile's canonical records must reject extra fields, trailing bytes, empty target arrays, wrong address widths, nonminimal headers, small integers expressed using tag 2, leading-zero magnitudes and indefinite forms below their thresholds. Rejecting an external serialization is not a new SRL operation or a new SRL error. The five operations still receive abstract requests. A codec's resource refusal must not misdescribe a valid but unsupported body as mathematically malformed. An encoded body with invalid span bounds is still an encoding of a `Body`; grounding is checked by operations, not by `E`.

## 2. Operating scope and evidence

These are **sequential reference profiles**. Start at the empty state. A supported retained start is an exact copy of a previously committed supported state with its catalogue membership preserved. All supported states are admissible and meet §4's state limits. No concurrent invocation, crash, recovery algorithm, deletion, migration or change of profile is claimed. Any realization supporting those behaviors needs a separately identified scope/profile and the corresponding SRL §7 argument.

The reference scope assumes a correct protected logical store and control metadata. They preserve exact bindings and catalogue membership independently of the delivery channel being checked. Faults may deny access, prevent delivery, or alter delivered evidence; they do not silently corrupt that protected reference state, the comparator, the evaluator or the profile. These are trust assumptions, not cryptographic guarantees. A future realization must justify how its actual storage and fault model establish them; hashing the delivery alone is insufficient.

Verification compares a delivered value against the protected retained value, byte for byte or body component by component, including order and repetitions. Occupancy is checked against the protected binding, including trustworthy vacancy. A catalogue observation is checked against protected catalogue membership and the exact body. No body is admitted merely because some bytes decode as it. `Put(E(r))` changes only `S`; decoding is never evidence of a past `Admit`.

For this reference model, complete conditions have the precise form:

```text
Condition_P(q,Σ) = a finite map from every relevant evidence slot to
    (permitted: Boolean, observation: Unknown | Absent | Bytes(v) | Body(r))
```

This dependent notation describes the relevant projection of one operation's `k`; a profile condition can equivalently contain entries for all possible slots. Extraneous entries have no effect. A complete `k` contains an entry for every relevant slot. Missing physical evidence maps to `Unknown`, not to an omitted condition entry or `Absent`. Actual observation payloads are included. The exact protected pre-state is already supplied by `Σ`.

Slot keys identify roles, not payload interpretations:

| Operation | Relevant slots after successful resource preflight |
| --- | --- |
| `Put(b)` | `occupancy(H(b))` |
| `Select(t)` | `source(0,a)` |
| `Admit(T,s)` | `source(p,a)` for each target position `p`, and `occupancy(H(E(T,s)))` |
| `Fetch(a)` | `source(0,a)` |
| `Lookup(a)` | `catalogue(a)` |

For source and occupancy slots, the expected observation is `Bytes(S[a])` if present, otherwise `Absent`. For catalogue slots, it is `Body(R[a])` if present, otherwise `Absent`. The map is one complete condition for the entire call; distinct target positions can have distinct delivery/access observations. Shared physical work is allowed only if it preserves these specified results.

The verifier uses this exhaustive table for each relevant slot:

| Condition | Established fact |
| --- | --- |
| `permitted=false` | `Unavailable`; do not use the denied observation |
| Permitted, `Unknown` | `Unavailable` |
| Permitted, non-unknown observation unequal to the expected observation, including wrong alternative/type | `IntegrityFailure` |
| Permitted observation equals expected `Absent`, source slot | `Unavailable` because a required source is absent |
| Permitted observation equals expected `Absent`, occupancy slot | Verified vacant address |
| Permitted observation equals expected `Absent`, catalogue slot | Verified catalogue nonmembership |
| Permitted observation equals expected present value | Verified exact source, incumbent or body, as applicable |

`Unknown` and `Absent` are internal evidence alternatives, not new public errors. This is a concrete mapping from observations to established facts. A realization must bind its observations to these alternatives independently of the result it wants to return. It cannot choose `k` after seeing a bad result to excuse it. Verified source evidence here includes the complete exact source; a different profile may justify partial reads without changing SRL.

## 3. Deterministic assessment

The following phases fix which failures become established. An error ranking by itself is not this assessment algorithm.

1. Validate only the abstract request structure against SRL `ValidRequest_P`. If invalid, return `Failure(InvalidRequest)` immediately. A negative offset or empty target sequence is invalid; a large natural offset is not.
2. Apply §4's resource preflight in its stated order. If a limit is exceeded, return `Failure(ResourceLimit)` immediately, without obtaining delivery observations. This is genuine declared resource refusal. Do not hash or encode a payload that already exceeds the preceding shape/size check. Short-circuited later defects are not asserted absent.
3. Assess all relevant evidence slots using §2. For `Select` and every `Admit` target independently establish `InvalidSpan` when `i ≥ j`, regardless of delivery. If source verification succeeds, also establish `InvalidSpan` when `j > length(S[a])`; otherwise, for in-bounds nonempty intervals, compute **the slice identifier** `H(S[a][i:j])` from the exact selected bytes and establish `InvalidSpan` if it differs from `h`. Do not check a slice on invalid bounds or infer a commitment mismatch from unknown evidence.
4. For a verified occupied write address compare proposed bytes with the exact incumbent. Establish `Collision` only if they differ. Verified vacancy is compatible. Do not replace occupancy verification with a digest match.
5. If any failures were established in phases 3–4, return the first member of the following list that belongs to that established set:

   ```text
   InvalidRequest, IntegrityFailure, InvalidSpan,
   Collision, Unavailable, ResourceLimit
   ```

   `InvalidRequest` and preflight `ResourceLimit` already terminate earlier phases; they are not retrospectively added. For example, an oversized request returns `ResourceLimit` without reading enough to discover an integrity defect. Within the evidence phase, independently known `i ≥ j` beats `Unavailable`. No universal SRL priority is implied.
6. Otherwise return the exact SRL §5 success and post-state. `Admit` validates every target over the same pre-state and publishes `S[c]=E(r)` and `R[c]=r` as one transition. Every failed operation preserves both maps; all successful reads preserve both maps. Repetition rechecks the current conditions.

Completeness follows by cases. After preflight, every evidence slot either supplies its exact prerequisite or one of the specified failures. Every source interval either meets bounds/identifier conditions or establishes `InvalidSpan`; every write address is vacant, equal, conflicting, or has failed evidence. With no established failure every success prerequisite holds. The fixed phase boundaries, exact functions and selection rule therefore determine one result for the same complete inputs. This is an abstract assessment argument, not a claim that an unexamined program implements it.

## 4. Fixed resource policy: SRL-SAMPLE-LIMITS-1/1.0.0

These deliberate sample limits belong to each complete profile. They are not measurements, minimum capacities or universal SRL limits. `MiB=2^20`, `GiB=2^30`. Equality with a maximum is allowed; only exceeding it refuses an operation. All arithmetic is exact.

| Quantity | Maximum |
| --- | --- |
| `Put` input bytes | 64 MiB |
| Statement bytes in `Admit` or supported `R` | 1 MiB |
| Targets per body in `Admit` or supported `R` | 100,000 |
| An offset in a `Select` or `Admit` request | `2^64−1` |
| Encoded body bytes for `Admit` or supported `R` | 256 MiB |
| Each retained `S` value, including record encodings | 256 MiB |
| Total retained `S` byte lengths | 1 GiB |
| Total `length(E(r))` over `R` | 1 GiB |
| Number of bindings in each map | 1,000,000 |
| Whole-operation logical byte reservation `W` | 1 GiB |

State totals are finite sums; the separate `R` total is logical accounting even if a physical realization shares storage. Supported `R` bodies meet all body limits. The policy does not redefine `Bytes`, `Nat`, `Body`, or `E`.

Preflight first checks request-only limits in table order (ignoring rows irrelevant to that operation), then the pre-state bounds, then computes the proposed write address if applicable, then checks projected state totals/binding counts, then `W`. For any admissible pre-state exceeding a declared state bound, every structurally valid operation returns `ResourceLimit` at this preflight. State bounds include each `S` value, map totals/counts and each `R` body's statement, target count, offsets and encoded length. This also defines the abstract refusal outside the supported state scope; it does not supply a repair transition or excuse an inadmissible state. The encoded size is calculated exactly from §1's headers and field lengths before encoding; a body already exceeding a preceding limit need not be encoded. No source-delivery observations are consumed during preflight. Correct protected control metadata supplies retained lengths, occupied keys and state totals even if access or delivery for the corresponding evidence slot will later fail. This explicit reference assumption is needed to make the reservation independently decidable; it must not be inferred from an unavailable backend in a different implementation model.

For projected state totals, an absent proposed `S` key reserves the entire new byte value and one key; an occupied key reserves no growth and remains subject to exact comparison later. A proposed new `R` key reserves the entire new encoding length and one key; an existing key reserves no growth and remains protected by compatibility and injective `E`. Reads reserve no state growth. A resource rejection does not overwrite an incumbent even when later collision evidence was not collected.

Define `L(a)=length(S[a])` if present and zero otherwise. For `t=(a,i,j,h)`, define `d(t)=j−i` if `0 ≤ i < j ≤ L(a)` and zero otherwise, and `C(t)=3L(a)+3d(t)`. The byte reservation is:

| Request | `W` |
| --- | --- |
| `Put(b)`, `a=H(b)` | `3 length(b) + 2L(a)` |
| `Select(t)` | `C(t)` |
| `Admit(T,s)`, `b=E(T,s)`, `c=H(b)` | `sum(C(t) for each position in T) + 4 length(b) + 2L(c)` |
| `Fetch(a)` | `3L(a)` |
| `Lookup(a)` | `2 length(E(R[a]))` if present, otherwise zero |

These formulas are a fixed logical reservation policy, not CPU, memory, elapsed-time or complexity measurements. Every repeated target is charged; no per-target allowance resets. The encoding and publication terms are charged once for the complete admission. Shared verification may reduce actual work but does not change the prescribed reservation or outcome. Administrative length/binding information used in these formulas establishes resource facts only; interval failures are assessed in phase 3.

The supported reference host has sufficient resources to complete operations within this policy, including comparison, hashing, encoding and atomic publication. Unexpected host exhaustion or protected-state corruption lies outside this sample fault scope and cannot be relabeled as a successful conforming call. A deployment needing additional memory, time, rate, access or persistence policies must state its own complete profile and condition mapping. Equal encoding/hash rules alone do not make two such deployments behaviorally identical.

## 5. Total addressing versus supported operations

Each named profile defines a total mathematical `H`, including an explicit completion outside its underlying algorithm's native input-length domain. The completion is intentionally collision-rich and carries **no cryptographic security claim**. Supported retained values, sources, slices and encodings are far below either native bound; all enabled operations use the ordinary named hash. A large well-typed request is refused by preflight, not truncated, wrapped or hashed under a different accidental rule. The completion does not permit storing enormous values or weaken exact occupied-address comparison.

An address contains no algorithm identifier. The full profile identifier must accompany an exchange context. There is no automatic profile negotiation or migration. The body schema version 1 is not a hash selector or a complete profile identifier. The two samples share `E`, but source addresses and commitments inside a body are profile-dependent; records generally differ between them.

## 6. Claim boundary and conformance obligations

These documents fix choices and justify encoding/assessment laws. [Vectors](VECTORS.md) provide reproducible finite checks and refusal scenarios. They do not certify a realization, prove all possible histories, establish hash security, or supply concurrency or crash durability.

A realization must still demonstrate SRL §7: its fixed abstraction, exact values and initialization; concrete evidence and fault assumptions; success/refusal/framing and deterministic complete conditions; preservation of retained history; and realization of enabled successes. Per-address locking by itself is not evidence of a transaction across all target reads and both catalogue/byte-store writes. Any added concurrency or recovery must justify the complete history, including pending calls, rather than merely restoring `WF` or decoding stored bytes.

## 7. Encoding reference and attribution

[RFC 8949](https://www.rfc-editor.org/rfc/rfc8949.html), especially §§3.1–3.2, 3.4.3 and 4.2, defines CBOR headers, indefinite forms, bignums and deterministic encoding terminology. The exact subset and huge-length exceptions above are fixed locally. This external codec reference does not change SRL-SPEC's self-contained contract.

Author: Shri Narayan Justin Ram; affiliation and publisher: Mushku Nobleworks. Copyright 2026 Mushku Nobleworks. This profile specification text is licensed under the repository's [CC BY 4.0](../LICENSE). No implementation, patent license, truth, origin or execution authority is asserted by these samples.
