---
title: Reproduce
description: The exact commands and digests that produce this site from the pinned gin commit.
---

# Reproduce

Every artifact on this site is re-creatable from the pinned commit with the
commands below. Nothing is hand-transcribed.

## 0. Toolchain

```bash
node --version          # v22.14.0
npm --version           # 10.9.2
go version              # go version go1.26.0 linux/amd64
npx sourcey --version   # sourcey v3.6.12
runx --version          # runx-cli 0.10.2
```

The `go` toolchain reports `go1.26.0` because `gin`'s `go.mod` declares
`go 1.26.0` and the Go toolchain switches automatically to satisfy it
(`GOTOOLCHAIN=auto`).

## 1. Pin the target

```bash
git clone https://github.com/gin-gonic/gin.git gin
cd gin
git checkout 0f09c3a9b4626d9fe9979cf4d0521d6ae32ab646
git rev-parse HEAD
# 0f09c3a9b4626d9fe9979cf4d0521d6ae32ab646
```

## 2. Take the godoc snapshot from that source

```bash
sourcey godoc -m . -p ./... -o godoc.json
```

Output (Sourcey v3.6.12):

```
Sourcey: wrote godoc snapshot for github.com/gin-gonic/gin
  Packages:    7
  Output:      godoc.json
```

Digest of the committed snapshot:

```bash
sha256sum godoc.json
# 91bfb81dff5fafadf8ea973ee99da82eb5bf0c82d0e0e854ea7e0a88bb070e15
```

The snapshot is a `runx`/`sourcey` **godoc snapshot**, `schema_version: 1`, with
`module_path: github.com/gin-gonic/gin` and `generated_at` recorded in the file.
It is committed to this repository so the site can be rebuilt on a JS-only host
with no Go toolchain, which is the workflow Sourcey documents for godoc tabs.

## 3. Build the site

```bash
sourcey build
```

`sourcey.config.ts` in this repository renders two tabs:

- **Guides** — the markdown pages in this repository (`introduction.md`,
  `coverage.md`, `gaps.md`, `reproduce.md`);
- **Go API** — `godoc({ module: "./gin-src", packages: ["./..."], mode: "snapshot",
  snapshot: "./godoc.json", includeTests: true })`.

`mode: "snapshot"` is deliberate: the published build must be byte-stable and
rebuildable without a Go toolchain. The live path was verified separately on the
build host with `mode: "auto"`, which re-runs `go list` + `go/parser` + `go/doc`
against the pinned clone and produces the same 7 packages.

## 4. Verify the published site

```bash
curl -sS -o /dev/null -w "%{http_code}\n" https://asporeteam.github.io/gin-sourcey-docs/
curl -sS https://asporeteam.github.io/gin-sourcey-docs/go/ | grep -c "gin-gonic"
```

The published site is the `dist/` output of step 3, committed to the `main` branch
of `ASporeTeam/gin-sourcey-docs` and served by GitHub Pages.

## 5. Re-measure the findings on the gaps page

```bash
# the four undocumented exported entries
python3 - <<'PY'
import json
d = json.load(open("godoc.json"))
for p in d["packages"]:
    for t in p.get("types", []):
        if not t.get("doc", "").strip():
            pos = t.get("position") or {}
            print("type", t["name"], pos.get("file"), pos.get("line"))
        for m in t.get("methods", []):
            if not m.get("doc", "").strip():
                pos = m.get("position") or {}
                print("method", t["name"] + "." + m["name"], pos.get("file"), pos.get("line"))
    for f in p.get("funcs", []):
        if not f.get("doc", "").strip():
            pos = f.get("position") or {}
            print("func", f["name"], pos.get("file"), pos.get("line"))
PY

# the README never mentions the QUERY method at this commit
grep -ic query README.md   # 0
```
