---
title: Maintainer-facing gaps
description: What a maintainer of github.com/gin-gonic/gin would want to know after reading the pinned commit's public surface.
---

# Maintainer-facing gaps

These are findings from reading the **pinned commit**
(`0f09c3a9b4626d9fe9979cf4d0521d6ae32ab646`) through the generated reference — not
a summary of what pages exist. Each one names a file and line in the pinned tree so
it can be checked in one click.

## 1. The new `QUERY` method is documented in code but nowhere else

The pinned commit is itself the `QUERY` support change
(`docs: include HTTP QUERY method in RouterGroup.Any (#4879)`). The code side is
good: `routergroup.go:14-17` declares the shim, `routergroup.go:176` adds
`(*RouterGroup).QUERY`, and `routergroup.go:181` lists `QUERY` in `Any`'s doc
comment.

The **README never mentions it**: `grep -ic query README.md` returns **0** at this
commit. A reader who learns about RFC 10008 `QUERY` support from the godoc
reference has no path from the README to it, and the README's route tables are the
place a Go developer actually looks. Adding the method to the README's routing
section (and to the `Any` list there, if the README has one) is a small, high-value
change.

## 2. `MethodQuery` is a hand-rolled shim that will need a migration plan

```go
// routergroup.go:14-17
// MethodQuery is the HTTP QUERY method defined by RFC 10008. It is declared
// here because the standard library does not provide http.MethodQuery yet.
const MethodQuery = "QUERY"
```

The constant is correct today, but it is a **duplicate of a stdlib symbol the
comment itself predicts will arrive**. When the standard library ships
`http.MethodQuery`, this shim becomes a second source of truth for the same method
name, and the two can drift (for example if the stdlib spelling or the `net/http`
method table changes). A maintainer note pointing at the upstream Go issue
(`golang/go#71459` tracks the `QUERY` method proposal) with a planned migration
step would turn a silent future conflict into a scheduled one.

## 3. Four exported entry points have no doc comment at all

Measured over the 431 exported entries in the snapshot, exactly four have an empty
doc comment:

| Symbol | Location | Why it matters |
|---|---|---|
| `type ContextKeyType int` | `context.go:52` | It is the type of the exported `ContextRequestKey` constant (`context.go:54`) and the type behind the documented `ContextKey` ("_gin-gonic/gin/contextkey", `context.go:50`). The doc comment stops one line short of the type it describes. |
| `(*gin.Engine).Handler` | `gin.go:257` | It is the `http.Handler` adapter for the engine (and the H2C path). It is the method a Go server integration needs, and it is the only public method on `Engine` with no comment. |
| `type SliceValidationError []error` | `binding/default_validator.go:21` | It is the error type returned by multi-field validation. Users must type-assert on it to report which field failed, and the doc comment exists only on its `Error()` method, not on the type. |
| `binding.MapFormWithTag` | `binding/form_mapping.go:40` | The exported, tag-aware form binder. Its unexported sibling `mapForm` (`binding/form_mapping.go:36`) is the same function with a fixed tag; the exported one has no comment, so the tag semantics (`form`, `json`, …) and the pointer requirements are undiscoverable. |

For a framework whose `binding` package is a stable extension point, that last one
is the costly omission: it is exported precisely so that users can call it.

## 4. `(*gin.Context).BindWith` is deprecated but still exported and documented

`deprecated.go:17` still ships `BindWith`, which logs a deprecation warning **on
every call** and then delegates to `MustBindWith`. The doc comment says
"Deprecated: Use MustBindWith or ShouldBindWith", which is correct, but the symbol
is still part of the public surface at this commit and will still show up in the
generated reference. A maintainer note about the removal horizon (the linked
upstream issue is #662) would let downstream code plan the migration.

## 5. `ginS` is a global-singleton package with wrapper-only documentation

The `ginS` package (26 exported functions) wraps a single process-global engine
created with `sync.OnceValue` (`ginS/gins.go:16-18`). Every exported function is
documented as "is a wrapper for Engine.X" — e.g. `LoadHTMLGlob`, `SetMode`,
`Run`, `Secure`, `LoadHTMLFiles`. Two maintainer-facing consequences:

- The doc text describes the *delegate*, not the *semantics of sharing one engine
  process-wide* — the part a user needs before choosing the package.
- The package is not in the module's public README surface, so the reference page is
  the only place its behaviour is described.

## 6. The `render` package's public surface is larger than its documentation

`render` contributes 23 types, 3 functions and 38 methods from 14 files — the
second-largest contributor in the snapshot. Its per-renderer docs are consistent
(`Render` implements `render.Render`), but the package-level relationship between
`render.Render`, `render.Render interface` implementations and the `Context.Render`
dispatch table is only discoverable by reading `context.go`. A maintainer-facing
"which renderer do I use for X" map would remove the need to read the dispatch code.

## How these were found

Every finding above was read out of the same snapshot that renders this site:
positions (`file:line`) come from Sourcey's godoc extraction, the "no doc comment"
set is the set of exported entries with an empty doc string in `godoc.json`, and the
README claim is a case-insensitive `grep` over the pinned `README.md` at that commit
(0 matches). Re-running the extraction on a later commit re-measures all of them.
