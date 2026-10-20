# SRL-SHA256-1, sample profile version 1.0.0

**Full profile identifier: `SRL-SHA256-1/1.0.0`. Recommended starting profile.** This is a concrete sequential sample for SRL-SPEC 1.0.0. Its complete definition is this document plus [COMMON-1 version 1.0.0](COMMON-1.md), including the encoding, evidence model, assessment, resource limits and operating scope. It is not a claim that an implementation conforms.

## Addressing

`Address` is every 32-byte sequence. Let `G(b)` be SHA-256 as defined by FIPS 180-4 (August 2015), applied to the byte sequence as its bit sequence in the standard byte order. The output is the standard 32 digest bytes. No text conversion, trailing newline, key, salt or profile prefix is added.

```text
H(b) = G(b)                  if length(b) < 2^61 bytes
       32 zero bytes         otherwise
```

SHA-256's standard message-length domain is fewer than `2^64` bits. For byte-aligned SRL values this is fewer than `2^61` bytes. The second branch explicitly completes the mathematical function over arbitrary finite `Bytes`. It is not SHA-256, is not collision-resistant, and is outside all supported retained values and enabled writes under COMMON-1. No implementation may wrap a bit length or silently truncate the input. Every enabled source, slice and encoding uses ordinary SHA-256.

For example:

```text
H(empty) = e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
H(616263) = ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
```

`616263` denotes the three raw bytes of ASCII `abc`, not six ASCII hexadecimal characters. See [vectors.json](vectors.json) for source, slice and body-identity bytes.

## Why this is the recommended starting point

SHA-256 provides a standardized algorithm definition and familiar verification tooling. Using it with the same exact CBOR encoding keeps the first integration focused on the five SRL operations and their evidence obligations. This is a tooling and specification choice; no benchmark, performance superiority, FIPS validation of a program or implementation certification is claimed.

`E` is exactly `SRL-CBOR-1/1.0.0`; identity is `H(E(r))`. Slice identifiers apply this same `H` to the exact selected bytes. The [BLAKE3 sample](SRL-RAW-1.md) is an alternative, with the same evidence and operating rules. The two profiles have distinct identifiers. They can share an encoding of an identical abstract body, but the profile-dependent addresses and commitments inside practical bodies generally make those bodies different. Neither profile permits interpreting an address without its profile context.

Resource limits and fault scope are deliberate sample choices. A deployment adding persistence, concurrency, different capacities or a different trust model must identify its complete behavior and demonstrate SRL §7, rather than call itself this exact profile solely because its hashes match. No origin, truth, authorship, confidentiality or execution authority follows from a successful admission.

## Algorithm reference

[NIST FIPS 180-4, August 2015](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf), §§5–6, fixes SHA-256. The input-length completion and operating limits above are local profile choices and carry no claim of being a FIPS-approved hash construction outside SHA-256's native domain.

Author: Shri Narayan Justin Ram; affiliation and publisher: Mushku Nobleworks. Copyright 2026 Mushku Nobleworks. Profile specification text: [CC BY 4.0](../LICENSE).
