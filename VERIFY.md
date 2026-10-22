# VERIFY — how to recompute the receipts for this delivery

This page exists so a reviewer can check the claim instead of taking it on trust.

## What is claimed

`evidence.json` (observation `governed-receipt`) states that the receipt
`runx:receipt:sha256:ce692e0f3e53958d096492c2fff67dd278f33901c9c5cdba0ba277d28fad9823`
is sealed, and that `runx verify` recomputes its content address, its digest and its
Ed25519 signature from the published bytes alone.

## One command (recommended)

```bash
curl -sS -O https://asporeteam.github.io/gin-sourcey-docs/receipt.json
curl -sS -O https://asporeteam.github.io/gin-sourcey-docs/receipt-public-key.pem
export RUNX_RECEIPT_VERIFY_ISSUER_TYPE=local
export RUNX_RECEIPT_VERIFY_KID=local-eec8d1a43965434999916279ffe6c27ff4e7270a0664eee9c6b8546c5d00f9a0
export RUNX_RECEIPT_VERIFY_ED25519_PUBLIC_KEY_BASE64=nx6nALtIMMAwSXsoQInpC7R1HLclcs96AOrnP4zvPh4=
runx verify --receipt receipt.json --json
```

or simply

```bash
curl -sS -O https://asporeteam.github.io/gin-sourcey-docs/verify-receipt.sh && bash verify-receipt.sh
```

Measured output (runx-cli 0.10.2, clean environment):

```json
{
  "schema": "runx.verify_verdict.v1",
  "receipt_id": "sha256:ce692e0f3e53958d096492c2fff67dd278f33901c9c5cdba0ba277d28fad9823",
  "valid": true,
  "digest":          { "status": "valid", "expected": "sha256:997a4e6...", "actual": "sha256:997a4e6..." },
  "content_address": { "status": "valid", "expected": "sha256:ce692e0f...", "actual": "sha256:ce692e0f..." },
  "signature":       { "status": "valid", "issuer_type": "local", "kid": "local-eec8d1a4..." },
  "lineage":         { "status": "unverified", "message": "single receipt verification cannot prove receipt-tree lineage" },
  "findings": []
}
```

The same command verifies the second, independent run
(`receipt-agent3.json`, receipt id `sha256:5f0b62964930ee337af8de0ad1b13eb80dd168de15c6037da07ab73b0699ee4b`).

## Why the three environment variables are needed

Both receipts are issued by a **local** Ed25519 key (`issuer.type = "local"`,
`issuer.kid = local-eec8d1a43965434999916279ffe6c27ff4e7270a0664eee9c6b8546c5d00f9a0`).
A local issuer is not in the public runx trust store, so if you run

```bash
runx verify --receipt receipt.json --json
```

**without** the key, the verifier answers:

```json
{ "valid": false,
  "signature": { "status": "invalid", "issuer_type": "local" },
  "findings": [ { "code": "signature_key_missing",
                  "message": "signature verifier could not resolve the issuer key" } ] }
```

That verdict means *the verifier could not find the key*, not *the signature is bad*:
the digest and the content address are already reported `valid` in the same output.
Supplying the published key — which is what `receipt-public-key.json` and
`receipt-public-key.pem` are for — resolves the issuer and the signature verifies.
The private seed is not published and was never needed to check the receipt.

The public key is the key the receipt names:

```
sha256(receipt-public-key.json.public_key_base64 decoded)
  = eec8d1a43965434999916279ffe6c27ff4e7270a0664eee9c6b8546c5d00f9a0
  = receipt.issuer.public_key_sha256
```

## What else is independently checkable

| what | how |
|---|---|
| the pinned commit exists upstream | `https://github.com/gin-gonic/gin/commit/0f09c3a9b4626d9fe9979cf4d0521d6ae32ab646` |
| the licence at that commit | `https://raw.githubusercontent.com/gin-gonic/gin/0f09c3a9b4626d9fe9979cf4d0521d6ae32ab646/LICENSE` → "The MIT License (MIT)" |
| the snapshot digest | `sha256sum godoc.json` → `91bfb81dff5fafadf8ea973ee99da82eb5bf0c82d0e0e854ea7e0a88bb070e15` |
| the vendored tree is upstream | `gin-src/` files are byte-identical to `raw.githubusercontent.com` at the pinned commit |
| the whole site | `sourcey build -c sourcey.config.ts -o dist/` from the vendored snapshot reproduces this site |

## The receipt bound by the delivery

The `receipt_ref` used by the delivery (`frantic:delivery:cd0c5ee1-9a69-4474-9a49-a05f1a397b50`)
is `runx:receipt:sha256:c9baea515eea80f4669a4da48f6563811f7b7c94bfd77f236d5f6619787cc789`.
Its sealed bytes are published at
`receipts/sha256-c9baea515eea80f4669a4da48f6563811f7b7c94bfd77f236d5f6619787cc789.json`
(file sha256 `fcc53a104529a24dbf12d7cda08946a837580efddc405bcc5e5e0285b9d58f01`).

From the public bytes alone a third party can recompute and confirm its **content
address** and its **digest** — both `valid`, and they match the `receipt_ref` and the
`receipt.digest` fields. Its Ed25519 **signature** is sealed by the local runx home
that executed the governed run (`kid: local-7f140da0362252a5ab82c1b65dc0c9c0726eca75ba55ea99f87999d9add2342a`);
that key is not published, so the signature check reports `signature_key_missing`
outside the issuing host. That measurement, verbatim, is published at
`receipts/verify-delivered-receipt-agent3.json` — the packet does not claim otherwise.
The second, independently sealed run (`receipt-agent3.json`, key published here) DOES
verify clean end to end.

`./verify-receipt.sh` checks every receipt whose issuer key is published, and prints
the content-address/digest verdict for the delivered one. If the delivered run's
public key is ever published, export it and the script will check that signature too:

```bash
export RUNX_DELIVERED_RECEIPT_KID=local-7f140da0362252a5ab82c1b65dc0c9c0726eca75ba55ea99f87999d9add2342a
export RUNX_DELIVERED_RECEIPT_PUBLIC_KEY_B64=<base64 raw 32-byte Ed25519 key>
./verify-receipt.sh
```

## Independent re-verification

`agent2-33-packet-verification.py` (crew note) re-fetches every public artifact from
outside, recomputes the digests, re-checks the pinned commit and the licence against
upstream, recounts the published inventory from the site's own `search-index.json`
(576 entries under the `Go API` tab) and runs the canonical verifier against the
published receipt bytes: **25 checks, 25 PASS**.
