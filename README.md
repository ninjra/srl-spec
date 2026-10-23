# SRL — Keep the source. Trace the claim.

**Keep original material intact. Attach notes and AI-generated claims to exact passages.**

You are reviewing a report. An AI summary makes a confident claim. A second reviewer disagrees. Which exact passage did each of them use, and can you still inspect the original?

SRL is a specification for building systems that keep the original bytes and store each claim separately, with references to the exact parts it points to. Reviewers can add different interpretations without rewriting the source or replacing earlier claims.

**The benefit:** a reader can inspect what a claim points to instead of relying on a summary alone. Checking that reference does not establish whether the claim is true or supported by the passage.

[**See a practical example**](#a-practical-example) · [**Choose-a-path guide**](#start-here) · [**Read the specification**](SPECIFICATION.md) · [**Sample verification tools**](tools/README.md) · [**Cite SRL**](#attribution-and-license)

## What would I use it for?

SRL is intended for people designing software where the original material must remain inspectable as interpretations accumulate:

| You are building… | SRL's contract helps you specify… |
| --- | --- |
| An AI research assistant or document review tool | How to retain the source behind an extracted claim and check its exact passage reference before saving the claim |
| A collaborative annotation system | How conflicting notes can point to the same source without overwriting it or each other |
| A collection of extracted claims for later review | How to preserve the exact source version and passage for each record, and explicitly refuse records whose required references cannot be verified |

SRL defines the storage and validation behavior behind these workflows. Your application supplies the interface, document parsing, search, interpretation and review decisions.

## A practical example

An original document contains this sentence:

> Delivery usually takes five days.

An AI attaches this claim to that passage:

> Delivery is guaranteed within a week.

A human reviewer attaches a different note to the same passage:

> This describes a usual delivery time; it does not make a guarantee.

In a system implementing SRL:

1. The original document is retained unchanged.
2. Each statement is stored separately with a reference to the exact passage in that retained document.
3. Before a record is accepted, all its passage references must pass the specified checks. A failed operation leaves the logical state unchanged.
4. Both statements can remain available for inspection. SRL does not decide which interpretation is correct.

The misleading AI claim could still have a valid passage reference. That distinction matters: **traceability lets someone check an interpretation; it does not certify the interpretation.** Later edits to a working copy do not silently redirect the old reference to different wording in that copy.

This is an illustrative workflow, not a demo application or runnable API. The [formal example below](#a-small-example) shows the corresponding byte-level operations and their prerequisites.

## What can I use today?

This repository contains **SRL-SPEC 1.0.0**, concrete sample profiles and offline verification tools. It does not yet supply a conforming SRL library, an annotation app or proof of an implementation's conformance.

- **Understand or evaluate the design:** read the example above, then [the contract's five operations](#five-operations).
- **Design an implementation:** use the [specification](SPECIFICATION.md) with a complete [sample profile](profiles/README.md). A profile fixes choices such as hashing, record encoding, limits and failure handling.
- **Inspect concrete bytes and rejection cases:** follow the [offline verification instructions](tools/README.md) and examine the [vectors and scenarios](profiles/VECTORS.md). This checker tests sample fixtures; it is not the library.
- **Read or cite the archived specification:** use the [PDF](SRL-SPEC-1.0.0.pdf) and [version-specific DOI](https://doi.org/10.5281/zenodo.23511373). The GitHub introduction and later sample profiles are separate from the original archived files.

## Start here

| Your question | Where to go |
| --- | --- |
| Why keep claims separate from their sources? | [Practical example](#a-practical-example) |
| How does this differ from existing annotation and provenance work? | [Related work and scope](RELATED_WORK.md) |
| What must a conforming implementation do? | [Formal specification](SPECIFICATION.md), especially §§4–7 |
| Which concrete encoding and hash choices can I examine? | [Sample profiles](profiles/README.md) |
| Can I run the sample checks? | [Verification setup and command](tools/README.md) |
| Where are the detailed qualifications? | [Clarifications](CLARIFICATIONS.md) |

## The technical terms, in plain language

- **Bytes:** the exact stored data. The core does not need to understand whether it is text, a PDF, an image or another format. Your application maps readable passages or other selections to those bytes.
- **Stand-off assertion:** a statement saved separately from the material it references.
- **Byte-span reference:** a reference to an exact interval within retained data, with the verification information required by the chosen profile.
- **Content address:** an identifier calculated from the data under a fixed profile. A matching hash alone does not establish exact equality, origin or truth.
- **Atomic admission:** accepting the complete record or leaving the logical state unchanged when the operation fails. A record with several references cannot be partly accepted.

The full name is **Stand-Off Epistemic Reflection Library**. “Reflection” means a separately recorded statement here; SRL does not interpret or judge that statement.

## Formal walkthrough and contract

SRL combines exact byte retention, ordered byte-span references and atomic admission of separate assertions in a small transition contract. It defines what a conforming implementation must preserve and how it must refuse requests. Verifying a byte reference does not establish the truth of the attached assertion.

## A small example

Under the successful-operation conditions in specification §§4–5 and §8—compatible occupied addresses, obtainable and verified required reads, and no applicable access, integrity or resource failure—the byte/assertion separation is:

| Component | Abstract request or binding | Successful result or retained value |
| --- | --- | --- |
| Retained source | `Put("abc")` | `Success(a)`, with `a = H("abc")` and `S[a] = "abc"` |
| Selected span | `t = (a, 1, 2, H("b"))` | Zero-based half-open slice `[1,2)`, with the end excluded |
| Selected bytes | `Select(a, 1, 2, H("b"))` | `Success("b")`; neither map changes |
| Separate statement | `s = "this byte is b"` | Opaque statement bytes, retained separately from the source |
| Admitted record | `Admit([t], s)` | `Success(c)`, with `r = ([t], s)`, `c = H(E(r))`, `R[c] = r` and `S[c] = E(r)` |

Admitting the span and statement leaves `"abc"` unchanged at `a`. Different assertions over the same span may coexist. These are abstract requests and outcomes, not a runnable API or proof of conformance.

> **Epistemic boundary:** Source bytes, reflection statements and admission verdicts remain distinct. Valid byte grounding establishes exact span selection under the selected profile; it does not establish semantic support, truth, authentication, permission or authority to execute instructions contained in bytes. The library treats statements as opaque and does not decide their truth.

## How the separation works

**SRL** (Stand-Off Epistemic Reflection Library) defines a schema-blind, content-addressed contract for keeping source bytes unchanged and recording assertions separately, with verifiable references to exact byte spans. Its state separates retained bytes (`S`) from admitted reflection records (`R`).

The example above separates the roles of source bytes and the assertion record; encoded record bytes are also retained:

```text
Retained bytes S                  Reflection records R
S[a] = "abc"                       R[c] = r
S[c] = E(r)                       r = ([t], s)
```

Here `a = H("abc")`, `c = H(E(r))`, `t = (a, 1, 2, H("b"))`, and `s = "this byte is b"`. `H` and `E` are the selected profile's addressing function and lossless record encoding. The walkthrough assumes compatible addresses and the other successful-operation conditions stated above.

## What the contract specifies

### Five operations

Every operation validates its request and performs one atomic transition over a fixed pre-state under the declared profile and complete applicable read, access, integrity and resource conditions. Successful outcomes require their specification guards and no blocking failure. The profile selects deterministically among applicable, established failures; no universal error precedence is imposed. Every failure preserves the complete pre-state. Select, Fetch and Lookup preserve it on success as well.

| Operation | Successful outcome | Behavioral role |
| --- | --- | --- |
| `Put(b)` | `Success(a)` | Retains finite bytes at `a = H(b)` without adding catalogue membership |
| `Select(a, i, j, h)` | `Success(S[a][i:j])` | Returns the exact nonempty retained span after source and span verification |
| `Admit(T, s)` | `Success(c)` | Verifies every target in nonempty ordered `T`; retains `E(r)` and admits `r = (T,s)` at `c = H(E(r))` |
| `Fetch(a)` | `Success(S[a])` | Obtains and verifies the complete retained byte sequence |
| `Lookup(a)` | `Success(R[a])` or `Success(NotInCatalogue)` | Returns established local catalogue membership or nonmembership; unavailable information cannot yield either successful answer |

### Core requirements

- **Schema-blind admission (R01):** Within declared resource limits and subject to specified failures, source admission accepts arbitrary finite bytes without source-domain parsing, schema negotiation, normalization or rewriting. The library may validate its own record structure.
- **Immutable retention (R02):** Existing bytes and admitted records remain unchanged. Equal digests do not establish equal bytes; conflicting occupied-address bindings are rejected.
- **Atomic grounding (R03):** Admission retains every exact ordered span and opaque statement. Every span must pass; one failed span rejects the complete record.
- **Epistemic separation (R04):** The epistemic boundary above applies to every reflection, not just the example.
- **Idempotent coexistence (R05):** Different assertions may coexist without overwriting earlier records. Repeated successful identical admission is idempotent under the fixed profile; current prerequisites still apply.
- **Deterministic, explicit failure (R06):** The same complete state, request, profile and operating conditions produce the same structural outcome. Unavailability or incomplete information cannot become established nonexistence, and resource limits cannot silently truncate results.
- **Occurrence preservation (R07):** Target positions and repeated occurrences are preserved. An absent relationship does not imply a negative semantic assertion.
- **Demonstrated conformance (R08):** A realization identifies its selected profiles, resource limits and operating scope and demonstrates the requirements, including rejection behavior. A hash, record or successful example alone is not proof of conformance.

Storage layout, addressing and lossless record encoding remain implementation choices within the specification's laws.

## Concrete sample profiles

Start with [SRL-SHA256-1/1.0.1](profiles/SRL-SHA256-1.md), the recommended SHA-256/CBOR sample. [SRL-RAW-1/1.0.1](profiles/SRL-RAW-1.md) supplies a BLAKE3/CBOR alternative. Both include exact encoding, evidence conditions, deterministic assessment, aggregate resource limits and a sequential reference scope, with [byte-level vectors and operation scenarios](profiles/VECTORS.md). They are profile specifications, not library implementations or certificates.

The [profile comparison and integration decisions](profiles/README.md) explain the choices. These profiles and the [clarification record](CLARIFICATIONS.md) are later repository additions; they are not included in the original v1.0.0 release or its Zenodo files. The published core specification and release artifacts retain their original bytes.

The [profile supplement](profiles/SUPPLEMENT.md) is independently versioned as 1.0.1, with a [portable offline checker and CI](tools/README.md). Its signed release tag is `profiles-v1.0.1`; use that tag for the exact supplement release files. The current branch includes this later introductory documentation update and its corresponding README checksum in `profiles/manifest.json`. The specification text remains CC BY 4.0; the new verification tools and associated utility/CI material use [MIT](LICENSE-TOOLS). Independent semantic review was not performed for the supplement and was excluded by the owner.

## Related work and scope

Related terminology includes content-addressed storage (CAS), byte-range annotation, out-of-band annotation metadata, immutable source retention, and idempotent successful admission.

SRL concerns the intersection of stand-off annotation, content addressing and provenance. Related reference points include W3C Web Annotation, IPLD, PROV, nanopublications and Hypothesis. The [related-work comparison](RELATED_WORK.md) identifies documented overlaps and scope differences. It makes no claim of performance superiority or interoperability.

## Reading the specification

Sections 1–7 of the [specification](SPECIFICATION.md) form the normative contract; §§8–10 are informative. The contract is self-contained and has no external normative dependency. This README and the related-work comparison introduce the scope and add no requirements.

Start with the profile declaration in §2.3, requests and failures in §4, operations in §5, and conformance in §7. Worked cases in §8 illustrate both success and refusal conditions. Grounding verifies byte references without deciding whether assertions are correct.

The [PDF](SRL-SPEC-1.0.0.pdf) renders the same specification. The [manifest](manifest.json) records SHA-256 hashes of the specification, PDF and license. Use [CITATION.cff](CITATION.cff) for citation metadata. The version-specific DOI is [10.5281/zenodo.23511373](https://doi.org/10.5281/zenodo.23511373).

## Release verification

The [v1.0.0 release](https://github.com/ninjra/srl-spec/releases/tag/v1.0.0) provides the PDF, integrity manifest, source bundle, detached SSH signatures and public verification key. The signed tag identifies the release commit. Signature verification instructions accompany the assets.

Release signing key fingerprint: `SHA256:QTt0VtNof5SP3I3/Kw8SU6cFhllY5xEzPKXRHrIFwKs`.

## Attribution and license

**Title:** *SRL: A Formal Specification for Byte-Anchored Assertions*

**Author:** Shri Narayan Justin Ram ([ORCID: 0009-0008-3593-2816](https://orcid.org/0009-0008-3593-2816)).

**Affiliation and publisher:** Mushku Nobleworks.

Copyright 2026 Mushku Nobleworks. The specification text is licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). See [LICENSE](LICENSE). This license statement concerns the specification text; it supplies no license claim about source or statement bytes entrusted to a realization.
