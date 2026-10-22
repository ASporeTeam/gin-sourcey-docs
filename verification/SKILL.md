---
name: sourcey-gin-docs-verify
description: Re-verify the published Sourcey documentation site for gin at the pinned commit, and record the checks in a sealed runx receipt.
---

# Verify the published Sourcey site for gin

This skill is the governed validation run for the Frantic bounty
"Publish Sourcey docs for a maintained OSS library" (bounty #33).

It re-fetches the **published** documentation site, checks that the pages a reviewer
would open are live, spot-checks documented symbols against the rendered pages, and
recomputes the digests of the artifacts that back the delivery. Everything it
prints is a fact it measured during the run, and the run itself is sealed into a
`runx.receipt.v1` receipt.

The skill performs no writes to the published site and spends nothing.
