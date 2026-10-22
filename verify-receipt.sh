#!/usr/bin/env bash
# verify-receipt.sh — recompute and verify the published runx receipts with the
# canonical runx CLI (>= 0.6.13; the crew's shared CLI prints "runx-cli 0.10.2").
#
# WHY THE ENV VARS MATTER
#   The receipts here are sealed by a LOCAL Ed25519 key (issuer.type = "local").
#   The verifier cannot resolve a local issuer from the public trust store, so
#   `runx verify --receipt receipt.json --json` on its own returns:
#       "valid": false,  findings: [{ "code": "signature_key_missing" }]
#   That is a KEY-RESOLUTION result, not a bad signature. Hand the verifier the
#   published issuer key and the SAME receipt verifies clean:
#       digest           valid
#       content address  valid
#       signature        valid   (Ed25519)
#       findings         []
#       "valid"          true
#
# The public key of that issuer is published next to this file:
#   receipt-public-key.json   (base64 raw Ed25519 key + its sha256)
#   receipt-public-key.pem    (the same key as an SPKI PEM)
#
# The receipt bound by the DELIVERY (receipts/sha256-c9baea51....json) was sealed
# by a different local key of the runx home that executed the governed run. Its
# issuer key is not published, so a third party can recompute its content
# address and digest from the public bytes (both valid) but cannot check its
# signature outside the issuing host. That is stated plainly in
# receipts/README.md and receipts/verify-delivered-receipt-agent3.json.
# If you have that issuer's public key, export it and this script will check
# the signature too:
#   export RUNX_DELIVERED_RECEIPT_PUBLIC_KEY_B64=<base64 raw 32-byte key>
#   export RUNX_DELIVERED_RECEIPT_KID=local-7f140da0362252a5ab82c1b65dc0c9c0726eca75ba55ea99f87999d9add2342a
#
# Usage:
#   ./verify-receipt.sh                 # verifies every receipt it can
#   RUNX=/path/to/runx ./verify-receipt.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
RUNX="${RUNX:-runx}"

# issuer of receipt.json / receipt-agent3.json (its public key is published here)
export RUNX_RECEIPT_VERIFY_ISSUER_TYPE=local
export RUNX_RECEIPT_VERIFY_KID=local-eec8d1a43965434999916279ffe6c27ff4e7270a0664eee9c6b8546c5d00f9a0
export RUNX_RECEIPT_VERIFY_ED25519_PUBLIC_KEY_BASE64=nx6nALtIMMAwSXsoQInpC7R1HLclcs96AOrnP4zvPh4=

DELIVERED="receipts/sha256-c9baea515eea80f4669a4da48f6563811f7b7c94bfd77f236d5f6619787cc789.json"

rc=0

run_one() {
  local file="$1" expect="$2"
  echo "=== ${file}"
  local out
  if out="$("${RUNX}" verify --receipt "${HERE}/${file}" --json 2>&1)"; then
    echo "${out}"
    if printf '%s' "${out}" | grep -q '"valid": true'; then
      echo "RESULT: valid=true  (${expect})"
    else
      echo "RESULT: NOT valid  (${expect})"
      rc=1
    fi
  else
    echo "${out}" >&2
    echo "RESULT: verify command failed  (${expect})" >&2
    rc=1
  fi
  echo
}

for f in receipt.json receipt-agent3.json; do
  [ -f "${HERE}/${f}" ] && run_one "$f" "signature verified with the published issuer key"
done

if [ -f "${HERE}/${DELIVERED}" ]; then
  if [ -n "${RUNX_DELIVERED_RECEIPT_PUBLIC_KEY_B64:-}" ]; then
    (
      export RUNX_RECEIPT_VERIFY_ISSUER_TYPE=local
      export RUNX_RECEIPT_VERIFY_KID="${RUNX_DELIVERED_RECEIPT_KID:-local-7f140da0362252a5ab82c1b65dc0c9c0726eca75ba55ea99f87999d9add2342a}"
      export RUNX_RECEIPT_VERIFY_ED25519_PUBLIC_KEY_BASE64="${RUNX_DELIVERED_RECEIPT_PUBLIC_KEY_B64}"
      run_one "${DELIVERED}" "signature verified with the delivered-run issuer key"
    )
  else
    echo "=== ${DELIVERED}"
    echo "(the issuer key of the delivered run is not published; content address + digest only)"
    "${RUNX}" verify --receipt "${HERE}/${DELIVERED}" --json 2>&1 | head -n 40
    echo
  fi
fi

if [ "${rc}" -eq 0 ]; then
  echo "ALL RECEIPTS WITH A PUBLISHED KEY VERIFIED (valid: true, no findings)."
else
  echo "AT LEAST ONE RECEIPT DID NOT VERIFY." >&2
fi
exit "${rc}"
