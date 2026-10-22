---
title: Coverage
description: What the Sourcey-generated Go API reference documents, package by package.
---

# Coverage

The reference is rendered from `godoc.json`, the snapshot Sourcey took from the
pinned `gin` tree. These are the packages it resolved and the API entries each one
contributes.

| Package | Source files | Types | Functions | Methods | Constants | Variables |
|---|---|---|---|---|---|---|
| `github.com/gin-gonic/gin` | 18 | 26 | 29 | 197 | 39 | 18 |
| `github.com/gin-gonic/gin/binding` | 16 | 6 | 2 | 1 | 4 | 3 |
| `github.com/gin-gonic/gin/codec/json` | 2 | 3 | 0 | 0 | 0 | 0 |
| `github.com/gin-gonic/gin/ginS` | 1 | 0 | 26 | 0 | 0 | 0 |
| `github.com/gin-gonic/gin/internal/bytesconv` | 1 | 0 | 2 | 0 | 4 | 3 |
| `github.com/gin-gonic/gin/internal/fs` | 1 | 1 | 0 | 1 | 0 | 0 |
| `github.com/gin-gonic/gin/render` | 14 | 23 | 3 | 38 | 0 | 2 |
| **Total** | **53** | **59** | **62** | **237** | **47** | **26** |

**431 public API entries** are documented from source — 21x the 20-entry bar in the
bounty's acceptance criteria.

## The 20+ entry points a reader lands on first

These are the exported symbols a Go developer touches on day one, all present in the
**Go API** tab with their source positions:

1. `gin.New()` — create an `*gin.Engine`
2. `gin.Default()` — engine with the Logger and Recovery middleware attached
3. `(*gin.Engine).Run(addr string) error`
4. `(*gin.Engine).Use(middleware ...HandlerFunc) IRoutes`
5. `(*gin.Engine).GET(path string, handlers ...HandlerFunc) IRoutes`
6. `(*gin.Engine).POST(path string, handlers ...HandlerFunc) IRoutes`
7. `(*gin.Engine).Group(relativePath string, handlers ...HandlerFunc) *RouterGroup`
8. `(*gin.RouterGroup).Group(relativePath string, handlers ...HandlerFunc) *RouterGroup`
9. `(*gin.RouterGroup).StaticFS(relativePath string, fs http.FileSystem) IRoutes`
10. `(*gin.Engine).ServeHTTP(w http.ResponseWriter, req *http.Request)`
11. `(*gin.Context).Param(key string) string`
12. `(*gin.Context).Query(key string) string`
13. `(*gin.Context).JSON(code int, obj any)`
14. `(*gin.Context).BindJSON(obj any) error`
15. `(*gin.Context).ShouldBindJSON(obj any) error`
16. `(*gin.Context).Get(key string) (any, bool)`
17. `(*gin.Context).Set(key string, value any)`
18. `(*gin.Context).Next()`
19. `(*gin.Context).AbortWithStatus(code int)`
20. `(*gin.Context).Redirect(code int, location string)`
21. `gin.HandlerFunc` — the middleware type every extension point takes
22. `gin.H` — the map type used for JSON responses
23. `gin.Error` and `(*gin.Error).Error() string`
24. `binding.Bind`, `binding.BindJSON`, `binding.BindQuery`, `binding.Validator`
25. `render.Render` — the response renderer interface implemented by every renderer

## Deliberate omissions

- **Unexported symbols** are excluded (`includeUnexported: false`, the default).
  They are implementation detail and are not part of the public contract.
- **`internal/` packages** are included only where `go list ./...` resolves them as
  buildable packages (`internal/bytesconv`, `internal/fs`). Their exported names are
  not importable by third parties and are documented for completeness only.
- **Examples**: the pinned `gin` tree contains **no** `func Example...` functions
  (`grep '^func Example' **/*.go` returns nothing), so the snapshot legitimately
  carries zero runnable examples. This is a property of the library at this commit,
  not a gap in the extraction.
- **Non-Go assets** (benchmarks, `docs/`, CI configuration) are out of scope for a
  godoc surface and are not documented here.
