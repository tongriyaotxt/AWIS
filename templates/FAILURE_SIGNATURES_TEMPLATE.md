# Failure Signatures

Append-only. Read at every session start. A recurring signature's **root
cause** jumps the priority queue — fix causes, not symptoms.

| Signature (how it manifests) | First seen | Root cause | Bucket (capability/flake/test-design) | Fix / workaround | Status |
|---|---|---|---|---|---|
| `<e.g. "pytest hangs >10min on test_sync">` | `<date/run>` | `<why>` | `<bucket>` | `<what resolved it>` | `<open/fixed>` |

## Rules

- One row per *reproducible* signature; merge duplicates, don't stack them.
- A signature is "fixed" only after the fix survives a fresh-environment run.
- Random/intermittent failures must be triaged into a bucket, never shrugged off:
  - **capability gap** → fix the implementation
  - **environment flake** → reduce concurrency / retry with backoff
  - **test design flaw** → fix the test and honestly annotate the change
