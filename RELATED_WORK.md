# Related work and scope

Informative context for the SRL specification, checked against the linked primary sources on 2026-10-20. This is a selected comparison of documented purposes and capabilities, not an exhaustive survey, ranking, performance benchmark or claim of interoperability. Established standards remain relevant reference points even when their publication dates are older.

| Reference | Documented related capability | SRL's corresponding scope |
| --- | --- | --- |
| [W3C Web Annotation Data Model](https://www.w3.org/TR/annotation-model/#data-position-selector) | Annotation bodies and targets, including a Data Position Selector over byte ranges | Retained content-addressed bytes, span commitments and atomic admission of ordered targets. Byte-range annotation itself is already established. |
| [IPLD Data Model](https://ipld.io/docs/data-model/) | Abstract data kinds including bytes and content-addressed links, with separate codecs for serialization | A byte-and-assertion catalogue transition contract, with profile-defined addressing and lossless record encoding. No IPLD interoperability is specified. |
| [W3C PROV-DM](https://www.w3.org/TR/prov-dm/) | Entities, activities, agents, derivation and attribution | Exact span references to retained bytes. Content identity in SRL does not establish origin, authorship or observation time. |
| [Nanopublication Guidelines](https://nanopub.net/guidelines/working_draft/) | Assertions, assertion provenance and publication information represented using RDF; the linked document is a working draft | Opaque statement bytes with exact source-span references; no RDF assertion or publication-metadata requirement. |
| [Hypothesis annotation types](https://web.hypothes.is/help/whats-the-difference-between-an-annotation-and-a-highlight/) | Working annotation software with passage-attached notes, highlights, page notes and replies | An abstract byte-level retention and admission contract. This SRL repository supplies neither an annotation interface nor a conforming library implementation. |

SRL concerns the intersection of stand-off annotation, content addressing and provenance. Its selected scope combines exact retained bytes, ordered span references, atomic admission, immutable/idempotent records and explicit failures while leaving statement meaning opaque. These comparisons describe overlaps and scope differences; they do not establish that the combination is unprecedented or superior.

The [specification](SPECIFICATION.md) defines SRL's requirements. This note and the [README](README.md) add none. No adapter, shared wire profile or cross-system conformance result is supplied.
