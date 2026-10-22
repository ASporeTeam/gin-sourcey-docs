#!/usr/bin/env python3
"""Governed validation run for the published Sourcey documentation site.

Fetches the published site over plain HTTPS, checks that every page a reviewer
would open answers 200, spot-checks documented symbols against the rendered
HTML, and recomputes the digests of the artifacts that back the delivery.

Prints one JSON object on stdout. No writes, no spending.
"""
import hashlib
import json
import os
import sys
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) spore-agent-sourcey-gin-verify/1.0"


def fetch(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001 - a transport error is a fact
        return 0, "error: %s" % exc


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    base = os.environ.get("RUNX_INPUT_BASE_URL") or \
        "https://asporeteam.github.io/gin-sourcey-docs"
    repo_root = os.environ.get("RUNX_INPUT_REPO_ROOT") or os.getcwd()
    base = base.rstrip("/")

    # The page list can be overridden for a re-publication on a different host
    # (e.g. the upstream project's own domain) via RUNX_INPUT_PAGES (JSON list).
    import json as _json
    _env_pages = os.environ.get("RUNX_INPUT_PAGES")
    pages = [
        "/",
        "/introduction/",
        "/coverage/",
        "/gaps/",
        "/reproduce/",
        "/go/",
        "/go/package-root/",
        "/go/pkg-binding/",
        "/go/pkg-render/",
        "/go/pkg-ginS/",
        "/go/pkg-codec-json/",
        "/go/pkg-internal-bytesconv/",
        "/go/pkg-internal-fs/",
    ]
    if _env_pages:
        try:
            pages = json.loads(_env_pages)
        except Exception:  # noqa: BLE001
            pass
    page_results = []
    for p in pages:
        status, body = fetch(base + p)
        page_results.append({
            "path": p,
            "status": status,
            "bytes": len(body),
        })

    # Spot-checks: a symbol is only counted as documented if the rendered
    # page for its package actually contains it.
    spot_checks = [
        ("/go/package-root/", "ShouldBindJSON",
         "(*Context).ShouldBindJSON is in the root package page"),
        ("/go/package-root/", "MethodQuery",
         "the RFC 10008 QUERY method constant is in the root package page"),
        ("/go/pkg-binding/", "MapFormWithTag",
         "the exported tag-aware form binder is in the binding package page"),
        ("/go/pkg-binding/", "SliceValidationError",
         "the exported multi-field validation error type is in the binding page"),
        ("/go/pkg-render/", "Render",
         "the render package documents the Render interface"),
        ("/", "0f09c3a9b4626d9fe9979cf4d0521d6ae32ab646",
         "the introduction page names the pinned commit"),
        ("/gaps/", "README never mentions it",
         "the gaps page states the README gap with its measurement"),
    ]
    _env_spot = os.environ.get("RUNX_INPUT_SPOT_CHECKS")
    if _env_spot:
        try:
            spot_checks = [tuple(x) for x in json.loads(_env_spot)]
        except Exception:  # noqa: BLE001
            pass
    checks = []
    for path, needle, why in spot_checks:
        status, body = fetch(base + path)
        checks.append({
            "path": path,
            "needle": needle,
            "why": why,
            "http_status": status,
            "found": needle in body,
        })

    artifacts = {}
    godoc = os.path.join(repo_root, "godoc.json")
    if os.path.isfile(godoc):
        artifacts["godoc.json"] = {"sha256": sha256_file(godoc),
                                    "bytes": os.path.getsize(godoc)}
    pinned = os.path.join(repo_root, "gin-src", "PINNED_COMMIT")
    if os.path.isfile(pinned):
        artifacts["gin-src/PINNED_COMMIT"] = {
            "sha256": sha256_file(pinned),
            "bytes": os.path.getsize(pinned),
            "commit": open(pinned).read().strip(),
        }
    manifest = os.path.join(repo_root, "dist-manifest.json")
    if os.path.isfile(manifest):
        artifacts["dist-manifest.json"] = {"sha256": sha256_file(manifest),
                                           "bytes": os.path.getsize(manifest)}

    result = {
        "base_url": base,
        "pages_checked": len(page_results),
        "pages_ok": sum(1 for p in page_results if p["status"] == 200),
        "page_results": page_results,
        "spot_checks_total": len(checks),
        "spot_checks_passed": sum(1 for c in checks if c["found"] and c["http_status"] == 200),
        "spot_checks": checks,
        "artifacts": artifacts,
        "verdict": "PASS" if (all(p["status"] == 200 for p in page_results)
                               and all(c["found"] for c in checks)) else "FAIL",
    }
    print(json.dumps({"message": json.dumps(result, sort_keys=True)}))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
