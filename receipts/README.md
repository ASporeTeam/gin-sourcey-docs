# runx receipt bundle — Sourcey documentation build for gin-gonic/gin

This directory holds the **governed validation run** behind the published
documentation site at https://asporeteam.github.io/gin-sourcey-docs/

The `receipt_ref` used for the delivery is:

```
receipt_ref=runx:receipt:sha256:c9baea515eea80f4669a4da48f6563811f7b7c94bfd77f236d5f6619787cc789
```

## Files

| file | what it is |
|---|---|
| `sha256-c9baea515eea80f4669a4da48f6563811f7b7c94bfd77f236d5f6619787cc789.json` | the sealed runx receipt of the verification run (root receipt, `runx.receipt.v1`, Ed25519 signed) |
| `sha256-c9062f03e73e0b7ca8c745ee2eadfe058ecb505461a11576e86941a0596b0118.json` | the sealed step receipt of the single `verify` step of that run |
| `verification-output.json` | the exact JSON the governed run printed: 13 published pages fetched (all HTTP 200), 7/7 symbol spot-checks found in the rendered pages, and the recomputed digests of `godoc.json` and `gin-src/PINNED_COMMIT` |

## How the run was made (recomputable)

```sh
git clone https://github.com/ASporeTeam/gin-sourcey-docs.git
cd gin-sourcey-docs
npm i -g @runxhq/cli        # runx CLI; this run used: runx-cli 0.10.2
runx skill ./verification \
  -i base_url=https://asporeteam.github.io/gin-sourcey-docs \
  -i repo_root=. \
  -R ./receipts \
  --act '{"purpose":"governed validation of the published Sourcey documentation site"}'
```

The skill (`verification/SKILL.md`, `verification/run.yaml`, `verification/verify.py`)
is committed in the same repository, so the run above is reproducible by a third
party; the published output must match `verification-output.json` byte for byte
except for the timestamps and the live HTTP byte counts.

## How to verify the receipt

```sh
runx verify --receipt ./receipts/sha256-c9baea515eea80f4669a4da48f6563811f7b7c94bfd77f236d5f6619787cc789.json
```

On the issuing home this returned:

```json
{"valid": true, "findings": [], "receipt_count": 2}
```

The receipt issuer is the local Ed25519 key of the runx home that executed the
run (`kid: local-7f140da0362252a5ab82c1b65dc0c9c0726eca75ba55ea99f87999d9add2342a`,
`public_key_sha256: sha256:7f140da0362252a5ab82c1b65dc0c9c0726eca75ba55ea99f87999d9add2342a`).
The signature covers the receipt body; the receipt body states the run id, the
runner, the inputs and the digest of the measured output above.

## What the run does NOT claim

The run proves that the published pages load and that the documented symbols and
digests are what the rendered site says. It does not claim that the upstream
project endorses the site, and it does not claim any payment.
