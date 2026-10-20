# SRL-RAW-1, sample profile version 1.0.1

**Full profile identifier: `SRL-RAW-1/1.0.1`.** This is a concrete sequential sample for SRL-SPEC 1.0.0, developed from the supplied BLAKE3/CBOR proposal. Its complete definition is this document plus [COMMON-1 version 1.0.1](COMMON-1.md), including the encoding, evidence model, assessment, resource limits and operating scope. It is not a claim that an implementation conforms.

## Addressing

`Address` is every 32-byte sequence. Let `G(b)` be the first 32 output bytes of BLAKE3 in its default **unkeyed hash mode**, using the standard initialization and flags. No key, derive-key context, text conversion, trailing newline or profile prefix is added.

```text
H(b) = G(b)                  if length(b) ≤ 2^64−1 bytes
       32 zero bytes         otherwise
```

The BLAKE3 authors' specification states a maximum input size of `2^64−1` bytes. The second branch explicitly completes the mathematical function over SRL's arbitrary finite `Bytes` domain. It is not BLAKE3, is not collision-resistant, and is outside all supported retained values and enabled writes under COMMON-1. No implementation may silently truncate a length to enter the first branch. Every enabled source, slice and encoding uses ordinary unkeyed BLAKE3 with 32-byte output.

For example, the empty source address is:

```text
af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262
```

This displays the raw digest bytes in their original order. It is not the hash of hexadecimal text. See [vectors.json](vectors.json) for exact source, slice and body-identity bytes.

## Compatibility and use

`E` is exactly `SRL-CBOR-1/1.0.0`. Record identity is `H(E(r))`; slice identifiers are `H` applied to the exact selected bytes. Ordered targets and opaque statement bytes are unchanged. Comparing hashes alone never substitutes for the exact evidence and occupied-address comparison required by COMMON-1.

This profile retains the proposal's BLAKE3, ordinary CBOR shape, order/repetition preservation, exact comparison, failure ranking and atomic admission. The [integration decisions](README.md#what-was-absorbed-and-adjusted) describe the independently specified corrections. In particular, offsets above 64 bits remain encodable; they are resource-refused by this sample's operations rather than removed from SRL's mathematical domain. The profile fixes the whole assessment process, not merely an error list.

Choose this sample when BLAKE3 tooling is already part of the intended environment. This document makes no performance comparison with another profile. It provides no Web Annotation interoperability, authenticity, confidentiality, timestamps or semantic truth guarantees. A production deployment must justify its concrete storage, fault and resource assumptions rather than infer them from this sample's name.

## Algorithm reference

[The BLAKE3 authors' specification](https://github.com/BLAKE3-team/BLAKE3-specs/blob/master/blake3.tex) defines the algorithm; the [official implementation and test vectors](https://github.com/BLAKE3-team/BLAKE3/tree/1.8.7) provide reproducibility context. The algorithm's default hash mode and first 32 bytes are fixed here; a future library release does not authorize changing this profile's function. Mathematical completion and operating limits are local profile choices.

Author: Shri Narayan Justin Ram; affiliation and publisher: Mushku Nobleworks. Copyright 2026 Mushku Nobleworks. Profile specification text: [CC BY 4.0](../LICENSE).
