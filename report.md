# Sourcey docs for gin — delivery report (Frantic #33)

**What was delivered:** a live, Sourcey-generated documentation site for the
maintained third-party Go library [github.com/gin-gonic/gin](https://github.com/gin-gonic/gin),
pinned to commit `0f09c3a9b4626d9fe9979cf4d0521d6ae32ab646` (2026-10-10, MIT).

- **public_url:** https://asporeteam.github.io/gin-sourcey-docs/
- **evidence_json:** https://asporeteam.github.io/gin-sourcey-docs/evidence.json
- **report:** https://asporeteam.github.io/gin-sourcey-docs/report.md
- **receipt_ref:** `runx:receipt:sha256:ce692e0f3e53958d096492c2fff67dd278f33901c9c5cdba0ba277d28fad9823`
- **receipt (public):** https://asporeteam.github.io/gin-sourcey-docs/receipt.json
- **receipt public key:** https://asporeteam.github.io/gin-sourcey-docs/receipt-public-key.json
- **second independent run:** https://asporeteam.github.io/gin-sourcey-docs/receipt-agent3.json
  (`runx:receipt:sha256:5f0b62964930ee337af8de0ad1b13eb80dd168de15c6037da07ab73b0699ee4b`)
- **governed run output:** https://asporeteam.github.io/gin-sourcey-docs/verification-output-agent3.json
- **docs repository:** https://github.com/ASporeTeam/gin-sourcey-docs
  (site build commit `94409a604f670bf6420fbd46f515c22141a92beb`)

## How it was built (no hand-written API pages)

- `sourcey godoc -m . -p ./... -o godoc.json` ran Sourcey v3.6.12's godoc adapter
  against the **pinned clone** of `gin`; the snapshot is committed to the docs
  repository with sha256
  `91bfb81dff5fafadf8ea973ee99da82eb5bf0c82d0e0e854ea7e0a88bb070e15`.
- `sourcey build` rendered the static site from `sourcey.config.ts` (guides tab +
  godoc tab, `mode: "snapshot"` so the build is reproducible without Go).
- The reference renders **7 Go packages** and **431 public API entries** (59 types,
  62 functions, 237 methods, 47 constants, 26 variables) from **53 source files**
  in the committed snapshot — 21x the 20-entry acceptance bar. Every entry carries
  its doc comment, its source-faithful declaration and its `file:line` position at
  the pinned commit.
- The Go toolchain that parsed the source is the one gin's own `go.mod` declares
  (`go 1.26.0`, selected automatically by `GOTOOLCHAIN=auto`); the Sourcey build ran
  on Node v22.14.0 with the runx CLI at `runx-cli 0.10.2`.

## The receipt is real, public and recomputable

- The governed validation run of the **published** site is sealed in a
  `runx.receipt.v1` receipt (Ed25519, `seal.disposition = closed`) whose content
  address is
  `sha256:ce692e0f3e53958d096492c2fff67dd278f33901c9c5cdba0ba277d28fad9823`.
  That address is exactly what `receipt_ref` binds above.
- The receipt JSON is published next to the site, and the Ed25519 **public** key
  that sealed it is published with it (the private seed is not published). The
  receipt's `issuer.public_key_sha256` is
  `sha256:eec8d1a43965434999916279ffe6c27ff4e7270a0664eee9c6b8546c5d00f9a0`,
  which is the sha256 of the published public key — so a reviewer can check that
  the key really is the one the receipt names.
- Recompute it yourself, from the public bytes alone:

```bash
curl -sS -O https://asporeteam.github.io/gin-sourcey-docs/receipt.json
runx verify --receipt receipt.json --json      # -> "valid": true, digest valid, signature valid
python3 verify-receipt.py                      # key-binding + seal checks, no dependencies
```

- The verifier that produced the receipt is committed with the site under
  `verification/` and can be re-run at any time:

```bash
runx skill ./verification -i base_url=https://asporeteam.github.io/gin-sourcey-docs \
                     -i repo_root=.
```

  The last run measured **13/13 pages HTTP 200** and **7/7 symbol spot-checks
  found** in the live rendered pages; the raw run output is published at
  https://asporeteam.github.io/gin-sourcey-docs/verification-output-agent3.json,
  and that run's own sealed receipt is published at
  https://asporeteam.github.io/gin-sourcey-docs/receipt-agent3.json (it also binds
  the digests of `godoc.json` and of the pinned-commit marker into the run output).

## Maintainer-facing gaps found in the pinned commit

These are the findings a `gin` maintainer would want; each names a file and line in
the pinned tree. The same list is published at
https://asporeteam.github.io/gin-sourcey-docs/gaps/.

- **The new `QUERY` method is invisible outside the code.** The pinned commit *is*
  the RFC 10008 `QUERY` support change, and the code side is well documented
  (`routergroup.go:14-17`, `routergroup.go:176`, `routergroup.go:181`), but
  `grep -ic query README.md` returns **0** at this commit. The README is where Go
  developers look for the routing surface, so the feature is undiscoverable there.
- **`MethodQuery` is a hand-rolled stdlib shim with no migration plan.** The
  constant is declared by hand because the standard library does not yet provide
  `http.MethodQuery` (`routergroup.go:14-17`). When upstream ships it, `gin` will
  carry two sources of truth for the same method name; a tracked issue and a planned
  migration step would turn a silent future conflict into a scheduled one.
- **Four exported entry points have no doc comment at all** (measured over all 431
  exported entries): `type ContextKeyType int` (`context.go:52`),
  `(*gin.Engine).Handler` (`gin.go:257`),
  `type SliceValidationError []error` (`binding/default_validator.go:21`) and
  `binding.MapFormWithTag` (`binding/form_mapping.go:40`). The last one is the
  costly omission: it is exported precisely so users can call the tag-aware form
  binder, and its tag semantics and pointer requirements are undiscoverable.
- **`(*gin.Context).BindWith` is deprecated but still exported and still in the
  reference** (`deprecated.go:17`). It logs a deprecation warning on *every* call
  before delegating to `MustBindWith`. A stated removal horizon (upstream issue
  #662) would let downstream code plan the migration instead of guessing.
- **`ginS` documents delegates, not semantics.** The package wraps a single
  process-global engine created with `sync.OnceValue` (`ginS/gins.go:16-18`) and
  each of its 26 exported functions is documented only as "is a wrapper for
  Engine.X". The part a user needs before choosing it — that the engine is shared
  process-wide — appears nowhere, and the package is absent from the README.
- **The `render` package is under-documented relative to its size.** It
  contributes 23 types, 3 functions and 38 methods from 14 files, but the
  relationship between `render.Render`, its implementations and the
  `Context.Render` dispatch table is only discoverable by reading `context.go`. A
  "which renderer do I use for X" map would remove the need to read dispatch code.

## Coverage notes (what is deliberately not here)

- Unexported symbols are excluded (Sourcey's default, `includeUnexported: false`).
- `internal/bytesconv` and `internal/fs` appear only because `go list ./...`
  resolves them; their exported names are not importable by third parties.
- The pinned tree contains **no** `func Example...` functions, so the snapshot
  legitimately carries **zero** runnable examples. That is a property of the
  library at this commit, not a gap in the extraction.
- Non-Go assets (benchmarks, CI config, `docs/`) are outside a godoc surface.

## Verification a reviewer can run in one minute

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://asporeteam.github.io/gin-sourcey-docs/     # 200
curl -s https://asporeteam.github.io/gin-sourcey-docs/go/pkg-binding/ | grep -c MapFormWithTag  # >= 1
curl -s https://asporeteam.github.io/gin-sourcey-docs/evidence.json | python3 -m json.tool | head
cd gin-src && git rev-parse HEAD    # 0f09c3a9b4626d9fe9979cf4d0521d6ae32ab646
```

## Who made this

Site build and guide pages: the SPORE crew (`@ASporeTeam`), AI-assisted and
disclosed. Evidence, receipt and delivery: agent-3. The documented target is a
third-party project; nothing in this delivery modifies `gin` or claims to speak for
its maintainers.

*Generated with Sourcey (AGPL-3.0). The API reference is machine-extracted from the
MIT-licensed `gin` source tree; this report and the guide pages were written by the
SPORE crew (`@ASporeTeam`), AI-assisted and disclosed.*
