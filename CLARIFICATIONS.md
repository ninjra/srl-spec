# SRL-SPEC 1.0.0 clarification and review record

This is informative repository guidance added after publication. It records the substance of subsequent review and points to concrete examples. It does not amend the normative [SRL-SPEC 1.0.0](SPECIFICATION.md), replace its published PDF, certify an implementation, or silently introduce a new core version.

## Compact notation and operation map

| Symbol or operation | Meaning |
| --- | --- |
| `P` | Fixed complete profile: addressing, encoding, evidence/assessment, resources and operating scope |
| `Σ=(S,R)` | Retained byte bindings and separately established admitted-body bindings |
| `t=(a,i,j,h)` | Source address, zero-based half-open byte interval and slice identifier/commitment |
| `r=(T,s)` | Nonempty ordered targets, preserving repetitions, and opaque statement bytes |
| `E(r)`; `H(b)` | Exact recoverable body encoding; profile-defined byte addressing function |
| `k` | Complete operation conditions sufficient, with `Σ`, `q` and `P`, to determine the result |
| `Put` | Retain bytes; never infer or add admission membership |
| `Select` | Verify and return the exact nonempty slice |
| `Admit` | Check all targets over one pre-state; atomically retain encoding and establish membership |
| `Fetch` | Verify and return the full retained byte value |
| `Lookup` | Return the exact body or established catalogue nonmembership; unknown evidence is failure |

The abstract semantics specify allowable results and effects. A realization must separately justify the mapping from concrete storage and observations to that state and those conditions under SRL §7. A profile is the bridge; naming a hash or publishing an error order alone does not supply it.

## Review dispositions

| Review concern | Assessment and concrete response |
| --- | --- |
| Conditions mention access/integrity/resources without an explicit evidence payload model | Useful clarification. Successful values themselves are already fixed by `Σ`; success cannot return arbitrary observed bytes. Conditions must nevertheless distinguish every observation that can change verification or failure selection. [COMMON-1 §2](profiles/COMMON-1.md#2-operating-scope-and-evidence) gives exact observation alternatives, payloads, slot identities and verification rules. Its §3 fixes assessment. The general core does not require every lawful profile to use this representation. |
| Encoded bytes might be mistaken for proof of admission | The core already distinguishes `S` and `R` in §§3, 5.3, 8 T05 and 9.4. The samples make the distinction operational: catalogue evidence is verified separately; `Put(E(r))` and decoding alone never establish membership. Corresponding vectors exercise this history. No biconditional between stored encoding and catalogue membership is added to `WF`. |
| A profile label or policy list could be mistaken for a complete profile | The core §2.3 says labels alone are insufficient. The new samples instantiate all required components, with exact domains, encoding recovery, condition slots, evidence mapping, assessment phases, aggregate resource formulas and reference fault scope. [Profile index](profiles/README.md). |
| Overlapping failures and precedence may still leave ambiguity | Retain the core's profile freedom. The samples specify which checks occur before refusal and which failures become established, then apply priority to that set. Unknown evidence never establishes a bounds or commitment contradiction. Resource preflight can stop before later defects are discovered. This is stronger guidance than an error ranking by itself. |
| “Digest” or “commitment” may imply cryptographic strength | In SRL the value `h` is exactly the profile's `H` applied to selected bytes; neither term implies injectivity, hiding or collision resistance. Samples use “slice identifier” operationally and retain “commitment” only with that definition. A future core editorial revision can harmonize vocabulary without changing the equality check or adding a security assumption. |
| “Complete relevant read” and “sufficient verified evidence” need concrete obligations | “Relevant” means facts used to justify this operation's success or an applicable refusal, not an exhaustive whole-store scan. “Sufficient” means evidence supporting the exact retained binding, interval or catalogue fact under the declared trust/fault assumptions. The sample's slot table fixes the relevant set; its verifier table fixes sufficient evidence for that scope. A different profile must provide an equally determinate justification rather than inherit the sample's protected-state assumption. |
| Cases may look like universal executable test vectors | SRL §8 explicitly makes cases informative and gives success/failure assumptions; collision and alternate-identifier cases are conditional. [VECTORS.md](profiles/VECTORS.md) separates actual fixed-hash vectors, condition-dependent operation scenarios, resource arithmetic and a different synthetic collision profile. None is universal evidence for every profile. |
| PDF extraction reportedly joins words or headings | Inspection of the repository's actual 10-page published PDF, including the first-page prose and dense failure/invariant tables, found visible spacing and readable layout. Native extraction of the first page retains the reported sentence's word boundaries; the reported `Thisconvention...` join was not reproduced. This observation concerns this exact artifact, not every PDF extractor or a general accessibility certification. The Markdown remains available as text. |

## Evidence completeness as a profile obligation

For `Step_P(Σ,q,k)`, a successful `Fetch(a)` must return `S[a]` and a successful `Lookup(a)` must return the prescribed catalogue result. Those values are not free variables missing from the abstract state. What must be complete is the information determining **whether verification/access/resources permit success, which failures are established, and which one is selected**. If two differing observations can change that answer, a lawful profile must distinguish them in its conditions or derive their relevant effect deterministically from complete inputs.

This does not prescribe a universal physical log, evidence packet or public API argument. The concrete observation-to-condition mapping must be justified independently of the claimed result (§7.1). A profile cannot hide nondeterminism by retrospectively declaring a different condition, treat unavailable data as absent, or redefine retained values to fit corrupted returns.

The sample condition map includes actual payloads and explicit missing/denied alternatives so two independent implementers have a precise example. That model assumes an independently correct protected reference state. A real deployment must demonstrate its own basis for exact verification; a matching hash alone does not discharge that obligation.

## Release and correction policy

The [v1.0.0 release](https://github.com/ninjra/srl-spec/releases/tag/v1.0.0) and [version DOI](https://doi.org/10.5281/zenodo.23511373) continue to identify the original published artifacts. These clarifications and profiles are later repository material, not retroactively part of that deposit. Any normative correction must be presented as a separately versioned successor with its changes stated explicitly. No current review establishes that the central state-transition model has a fatal inconsistency, or that a supplied allegation is true merely because it was submitted.

Author: Shri Narayan Justin Ram; affiliation and publisher: Mushku Nobleworks. Copyright 2026 Mushku Nobleworks. This explanatory specification text: [CC BY 4.0](LICENSE).
