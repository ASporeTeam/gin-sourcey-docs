#!/usr/bin/env python3
"""Independent, dependency-light checks on the public runx receipt for #33.

This does NOT re-implement runx.receipt.c14n.v1 (that canonicalisation is
implemented by the runx CLI itself).  What it checks here is everything a
reviewer can check without the CLI:

  1. the published public key is the key the receipt names
     (sha256(public_key) == receipt.issuer.public_key_sha256)
  2. the receipt is sealed, not failed (seal.disposition == "closed")
  3. the receipt id in the file is the id we publish as receipt_ref
  4. the receipt is well formed against the runx.receipt.v1 schema shape

For the Ed25519 signature and the receipt tree, run the canonical verifier:

    runx verify --receipt receipt.json --json      # -> "valid": true

Usage:  python3 verify-receipt.py [receipt.json] [receipt-public-key.json]
"""
import base64
import hashlib
import json
import os
import sys


def b64d(s):
    s = s.replace("-", "+").replace("_", "/")
    return base64.b64decode(s + "=" * (-len(s) % 4))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    rpath = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "receipt.json")
    kpath = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "receipt-public-key.json")
    receipt = json.load(open(rpath))
    key = json.load(open(kpath))

    state = {"ok": True}

    def check(name, cond, detail=""):
        state["ok"] = state["ok"] and bool(cond)
        print("%-5s %s%s" % ("PASS" if cond else "FAIL", name, ("  " + detail) if detail else ""))

    pub = b64d(key["public_key_base64"])
    check("public key is the key the receipt names",
          "sha256:" + hashlib.sha256(pub).hexdigest() == receipt["issuer"]["public_key_sha256"],
          receipt["issuer"]["public_key_sha256"])
    check("receipt schema is runx.receipt.v1", receipt.get("schema") == "runx.receipt.v1")
    check("receipt is sealed (not failed)",
          receipt.get("seal", {}).get("disposition") == "closed",
          str(receipt.get("seal", {}).get("disposition")))
    check("receipt id matches the published receipt_ref",
          receipt.get("id", "").split(":", 1)[-1] == key.get("receipt_id", "").split(":", 1)[-1],
          receipt.get("id", ""))
    check("signature is Ed25519", receipt.get("signature", {}).get("alg") == "Ed25519")
    check("receipt carries a content digest",
          str(receipt.get("digest", "")).startswith("sha256:"), str(receipt.get("digest")))

    print()
    print("signature + tree verification (canonical):")
    print("  runx verify --receipt receipt.json --json")
    print()
    print("RESULT:", "PASS" if state["ok"] else "FAIL")
    return 0 if state["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
